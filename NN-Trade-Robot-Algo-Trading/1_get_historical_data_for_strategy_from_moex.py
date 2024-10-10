exit(777)  # To prevent running the code, otherwise it will overwrite results

import asyncio
import aiohttp
import aiomoex
import functions
import os
import pandas as pd
from datetime import datetime, timedelta
from my_config.trade_config import Config  # Configuration file for the trading robot


async def get_candles(session, ticker, timeframes, start, end):
    """Function to get candles from MOEX."""
    for timeframe in timeframes:
        tf = functions.get_timeframe_moex(timeframe)
        data = await aiomoex.get_market_candles(session, ticker, interval=tf, start=start, end=end)  # M10
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['begin'], format='%Y-%m-%d %H:%M:%S')
        # For M1, M10, H1 - adjust the candle date to the correct format
        if tf in [1, 10, 60]:
            df['datetime'] = df['datetime'].apply(lambda x: x + timedelta(minutes=tf))
        df = df[["datetime", "open", "high", "low", "close", "volume"]].copy()
        df.to_csv(os.path.join("csv", f"{ticker}_{timeframe}.csv"), index=False, encoding='utf-8', sep=',')
        print(f"{ticker} {tf}:")
        print(df)


async def get_all_historical_candles(portfolio, timeframes, start, end):
    """Starting asynchronous task to fetch historical data for each ticker in the portfolio."""
    async with aiohttp.ClientSession() as session:
        strategy_tasks = []
        for instrument in portfolio:
            strategy_tasks.append(asyncio.create_task(get_candles(session, instrument, timeframes, start, end)))
        await asyncio.gather(*strategy_tasks)


if __name__ == "__main__":

    # Applying settings from config.py
    portfolio = Config.portfolio  # Tickers for which we download historical data
    timeframe_0 = Config.timeframe_0  # Timeframe for training the neural network - input
    timeframe_1 = Config.timeframe_1  # Timeframe for training the neural network - output
    start = Config.start  # From what date we download historical data from MOEX
    end = datetime.now().strftime("%Y-%m-%d")  # Up to today

    # Creating necessary directories
    functions.create_some_folders(timeframes=[timeframe_0, timeframe_1])

    # Launching the asynchronous loop to fetch historical data
    loop = asyncio.get_event_loop()  # Create a loop
    task = loop.create_task(  # Add one task to the loop
        get_all_historical_candles(  # Start fetching historical data from MOEX
            portfolio=portfolio,
            timeframes=[timeframe_0, timeframe_1],  # For which timeframes we download data
            start=start,
            end=end,
        )
    )
    loop.run_until_complete(task)  # Wait for the loop to finish executing