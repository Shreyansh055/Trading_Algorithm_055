"""
    This code implements a live strategy. We asynchronously retrieve historical data from MOEX once and treat subsequent data as live.
    Since we get it for free, there's a 15-minute delay in the data.

    We use a neural network to predict when to enter a trade:
    - We choose the neural network at step #3 based on the results of loss, accuracy, val_loss, val_accuracy.
    - We open a market position as soon as the neural network gives a class 1 signal – buy with 1 lot.
    - No stop loss, as we close the position at the next +1 bar of the higher timeframe at market price.
"""

import asyncio
import os.path

import aiohttp
import aiomoex
import logging
import functions
import functions_nn
import pandas as pd
import numpy as np
from aiohttp import ClientSession
from datetime import datetime, timedelta
from typing import List, Optional

from FinamPy import FinamPy  # Connect to Finam API for placing buy/sell orders
from FinamPy.proto.tradeapi.v1.common_pb2 import BUY_SELL_BUY, BUY_SELL_SELL

from my_config.Config import Config as ConfigAPI  # Finam API config file
from my_config.trade_config import Config  # Trade robot config file

from keras.models import load_model
from keras.utils.image_utils import img_to_array


logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HackathonFinamStrategy:
    """This class implements our trading strategy."""

    def __init__(
        self,
        ticker: str,
        timeframe: str,
        days_back: int,
        check_interval: int,
        session: Optional[ClientSession],
        trading_hours_start: str,
        trading_hours_end: str,
        security_board: str,
        client_id: str,
    ):
        self.account_id = None
        self.ticker = ticker
        self.timeframe = timeframe
        self.days_back = days_back
        self.check_interval = check_interval
        self.session = session
        self.candles: List[List] = []
        self.live_mode = False
        self.trading_hours_start = trading_hours_start
        self.trading_hours_end = trading_hours_end
        self.security_board = security_board
        self.client_id = client_id
        self.order_time = None
        self.in_position = False

    async def get_all_candles(self, start, end):
        """Function to get candles from MOEX."""
        tf = functions.get_timeframe_moex(self.timeframe)
        data = await aiomoex.get_market_candles(self.session, self.ticker, interval=tf, start=start, end=end)  # M10
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['begin'], format='%Y-%m-%d %H:%M:%S')
        # For M1, M10, H1 - correct the candle's date format
        if tf in [1, 10, 60]:
            df['datetime'] = df['datetime'].apply(lambda x: x + timedelta(minutes=tf))
        df = df[["datetime", "open", "high", "low", "close", "volume"]].copy()
        # Except for the last candle, as its volume may change in the market
        df = df[:-1]
        return df.values.tolist()

    async def get_historical_data(self, model, fp_provider):
        """Retrieve historical data for the ticker."""
        logger.debug("Fetching historical data for ticker: %s", self.ticker)
        start = (datetime.now().date()-timedelta(days=self.days_back)).strftime("%Y-%m-%d")
        end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _candles = await self.get_all_candles(start=start, end=end)
        for candle in _candles:
            if candle not in self.candles:
                self.candles.append(candle)
                logger.debug("- Found %s - ticker: %s - live: %s", candle, self.ticker, self.live_mode)

                # If already in live mode
                if self.live_mode:
                    await self.live_check_can_we_open_position(model, fp_provider)

    async def live_check_can_we_open_position(self, model, fp_provider):
        """In live mode, check if we can open a position based on the neural network's class 1 signal."""
        # Create current image to send to the neural network

        df = pd.DataFrame(self.candles, columns=["datetime", "open", "high", "low", "close", "volume"])
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')

        period_sma_slow = 64
        period_sma_fast = 16
        draw_window = 128  # Data window
        steps_skip = 16  # Step for window shift
        draw_size = 128  # Size of the square image

        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
        df['sma_fast'] = df['close'].rolling(period_sma_fast).mean()  # Create fast SMA
        df['sma_slow'] = df['close'].rolling(period_sma_slow).mean()  # Create slow SMA

        df.dropna(inplace=True)  # Remove all NULL values

        df_in = df.copy()
        _close_in = df_in["close"].tolist()
        sma_fast = df_in["sma_fast"].tolist()
        sma_slow = df_in["sma_slow"].tolist()
        j = len(_close_in)

        _sma_fast_list = sma_fast[j - draw_window:j]
        _sma_slow_list = sma_slow[j - draw_window:j]
        _closes_list = _close_in[j - draw_window:j]

        # Generate image for neural network training/test
        img = functions_nn.generate_img(_sma_fast_list, _sma_slow_list, _closes_list, draw_window)

        # Send the generated image to the neural network
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        _predict = model.predict(img_array, verbose=0)
        _class = 0
        if _predict[0][1] >= 0: _class = 1
        print("Predicted: ", model.predict(img_array), " class = ", _class)

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Now implement simple trading logic
        if not self.in_position:  # If no open position
            if _class == 1:
                # Buy if we haven't yet and the neural network predicts growth
                rez = fp_provider.new_order(client_id=self.client_id, security_board=self.security_board,
                                            security_code=self.ticker,
                                            buy_sell=BUY_SELL_BUY, quantity=1,
                                            use_credit=True,
                                            )

                self.order_time = datetime.now()
                self.in_position = True
                print(f"Placed a buy order for 1 lot of {self.ticker}:", rez)
                print("\t - transaction:", rez.transaction_id)
                print("\t - time:", self.order_time)
        else:  # If there is an open position, check if it's time to close it
            _now = datetime.now()
            _timeframe_1 = Config.timeframe_1  # Higher timeframe
            _delta = functions.get_timeframe_moex(tf=_timeframe_1)
            if _now >= self.order_time + timedelta(minutes=_delta):
                # Sell if enough time has passed +1 bar of the higher timeframe
                rez = fp_provider.new_order(client_id=self.client_id, security_board=self.security_board,
                                            security_code=self.ticker,
                                            buy_sell=BUY_SELL_SELL, quantity=1,
                                            use_credit=True,
                                            )
                self.order_time = None
                self.in_position = False
                print(f"Placed a sell order for 1 lot of {self.ticker}:", rez)
                print("\t - transaction:", rez.transaction_id)
                print("\t - time:", self.order_time)
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    async def ensure_market_open(self):
        """Wait for the market to open. Ignores weekends and holidays."""
        is_trading_hours = False
        while not is_trading_hours:
            logger.debug("Waiting for market to open. ticker=%s", self.ticker)
            now = datetime.now()
            now_start = datetime.fromisoformat(now.strftime("%Y-%m-%d") + " " + self.trading_hours_start)
            now_end = datetime.fromisoformat(now.strftime("%Y-%m-%d") + " " + self.trading_hours_end)
            if now_start <= now <= now_end: is_trading_hours = True
            if not is_trading_hours: await asyncio.sleep(60)

    async def main_cycle(self, model, fp_provider):
        """Main live strategy cycle."""
        while True:
            try:
                await self.get_historical_data(model, fp_provider)  # Retrieve historical data from MOEX

                if not self.live_mode: self.live_mode = True  # Switch to live mode

                # Signals for buy/sell are handled in live_check_can_we_open