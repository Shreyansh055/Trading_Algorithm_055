"""
In this code, we prepare data for training the neural network.
We generate images according to the following algorithm:
1. Take the image of the closing price chart + SMA1 + SMA2 for a certain
interval on timeframe_0.
2. If the closing price on the higher timeframe_1 > closing price of the previous candle on the higher
timeframe_1, then assign class 1 to this image, otherwise class 0.
P.S. SMA1, SMA2 - moving averages
Author: Oleg Shpagin
Github: https://github.com/WISEPLAT
Telegram: https://t.me/OlegSh777
"""

exit(777)  # To prevent running the code, otherwise it will overwrite results

import functions
import functions_nn
import os
import matplotlib.pyplot as plt
from my_config.trade_config import Config  # Configuration file for the trading robot


if __name__ == "__main__":
    # Applying settings from config.py
    portfolio = Config.training_NN  # Tickers for which we train the neural network
    timeframe_0 = Config.timeframe_0  # Timeframe for training the neural network - input
    timeframe_1 = Config.timeframe_1  # Timeframe for training the neural network - output

    # Parameters for drawing images
    period_sma_slow = Config.period_sma_slow  # Period of the slow SMA
    period_sma_fast = Config.period_sma_fast  # Period of the fast SMA
    draw_window = Config.draw_window  # Data window
    steps_skip = Config.steps_skip  # Step for shifting the data window
    draw_size = Config.draw_size  # Size of the image side

    # Creating necessary directories
    functions.create_some_folders(timeframes=[timeframe_0], classes=["0", "1"])

    for ticker in portfolio:

        # Reading data for training the neural network - output - timeframe_1
        df_out = functions_nn.get_df_t1(ticker, timeframe_1)
        # print(df_out)
        _date_out = df_out["datetime"].tolist()
        _date_out_index = {_date_out[i]: i for i in range(len(_date_out))}  # {date: index}
        _close_out = df_out["close"].tolist()

        # Reading data for training the neural network - input - timeframe_0
        df_in = functions_nn.get_df_tf0(ticker, timeframe_0, period_sma_fast, period_sma_slow)
        # print(df_in)
        _date_in = df_in["datetime"].tolist()
        _close_in = df_in["close"].tolist()
        sma_fast = df_in["sma_fast"].tolist()
        sma_slow = df_in["sma_slow"].tolist()

        # # Output on the chart Close + SMA of the last 200 values
        # df_in[['close', 'sma_fast', 'sma_slow']].iloc[-200:].plot(label='df', figsize=(16, 8))
        # plt.show()

        _steps, j = 0, 0
        # Draw images only for the lower TF
        for _date in _date_in:
            if _date in _date_out:  # If the date of the lower TF is present in the dates of the higher TF
                _steps += 1
                j += 1
                if _steps >= steps_skip and j >= draw_window:
                    _steps = 0

                    # Form the image for the neural network with reference to the date and ticker with step steps_skip
                    # Size [draw_size, draw_size]
                    _sma_fast_list = sma_fast[j-draw_window:j]
                    _sma_slow_list = sma_slow[j-draw_window:j]
                    _closes_list = _close_in[j-draw_window:j]

                    # Generating an image for training/testing the neural network
                    img = functions_nn.generate_img(_sma_fast_list, _sma_slow_list, _closes_list, draw_window)
                    # img.show()  # Show the generated image

                    _date_str = _date.strftime("%Y_%m_%d_%H_%M_%S")
                    _filename = f"{ticker}-{timeframe_0}-{_date_str}.png"
                    _path = os.path.join("NN", f"training_dataset_{timeframe_0}")

                    # Performing classification of images
                    # if data.close[0] > data.close[-1]:
                    if _close_out[_date_out_index[_date]] > _close_out[_date_out_index[_date]-1]:
                        _path = os.path.join(_path, "1")
                    else:
                        _path = os.path.join(_path, "0")

                    img.save(os.path.join(_path, _filename))
                print(ticker, _date)  # Output the ticker and date
