import os
import pandas as pd
from PIL import Image, ImageDraw

cur_run_folder = os.path.abspath(os.getcwd())  # Current directory

def get_df_tf0(ticker, timeframe_0, period_sma_fast, period_sma_slow):
    """Read data for training the neural network - input - timeframe_0"""
    _filename = os.path.join(os.path.join(cur_run_folder, "csv"), f"{ticker}_{timeframe_0}.csv")
    df = pd.read_csv(_filename, sep=',')  # , index_col='datetime')
    if timeframe_0 in ["M1", "M10", "H1"]:
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    else:
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d')
    df['sma_fast'] = df['close'].rolling(period_sma_fast).mean()  # Create fast SMA
    df['sma_slow'] = df['close'].rolling(period_sma_slow).mean()  # Create slow SMA
    df.dropna(inplace=True)  # Remove all NULL values
    return df.copy()

def get_df_t1(ticker, timeframe_1):
    """Read data for training the neural network - output - timeframe_1"""
    _filename = os.path.join(os.path.join(cur_run_folder, "csv"), f"{ticker}_{timeframe_1}.csv")
    df = pd.read_csv(_filename, sep=',')  # , index_col='datetime')
    if timeframe_1 in ["M1", "M10", "H1"]:
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    else:
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d')
    return df.copy()

def generate_img(_sma_fast_list, _sma_slow_list, _closes_list, draw_window):
    """Generate an image for training/testing the neural network"""
    _max = max(max(_sma_fast_list), max(_sma_slow_list), max(_closes_list))
    _min = min(min(_sma_fast_list), min(_sma_slow_list), min(_closes_list))
    _delta_h = _max - _min
    _k_h = (draw_window - 1) / _delta_h  # Scaling coefficient for _h to fit in square
    w, h = draw_window, draw_window

    # Creating a new Image object - https://www.geeksforgeeks.org/python-pil-imagedraw-draw-line/
    img = Image.new("RGB", (w, h))
    img1 = ImageDraw.Draw(img)
    for i in range(1, w):
        # We will use lines for scaling - we can also use points
        # Output price
        _h_1 = int((_closes_list[i - 1] - _min) * _k_h)
        _h = int((_closes_list[i] - _min) * _k_h)
        shape = [(i - 1, _h_1), (i, _h)]
        img1.line(shape, fill="red", width=0)
        # Output fast SMA
        _h_1 = int((_sma_fast_list[i - 1] - _min) * _k_h)
        _h = int((_sma_fast_list[i] - _min) * _k_h)
        shape = [(i - 1, _h_1), (i, _h)]
        img1.line(shape, fill="blue", width=0)
        # Output slow SMA
        _h_1 = int((_sma_slow_list[i - 1] - _min) * _k_h)
        _h = int((_sma_slow_list[i] - _min) * _k_h)
        shape = [(i - 1, _h_1), (i, _h)]
        img1.line(shape, fill="green", width=0)
    return img
