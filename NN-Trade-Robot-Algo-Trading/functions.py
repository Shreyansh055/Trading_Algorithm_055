import datetime
import math
import os
import sys

def get_timeframe_moex(tf, rv=False):
    """Function to get the type of timeframe depending on the direction"""
    # - integer 1 (1 minute), 10 (10 minutes), 60 (1 hour), 24 (1 day), 7 (1 week), 31 (1 month), or 4 (1 quarter)
    tfs = {"M1": 1, "M10": 10, "H1": 60, "D1": 24, "W1": 7, "MN1": 31, "Q1": 4}
    if rv: 
        tfs = {1: "M1", 10: "M10", 60: "H1", 24: "D1", 7: "W1", 31: "MN1", 4: "Q1"}  # Reverse if needed
    if tf in tfs: 
        return tfs[tf]
    return False

def get_future_key(key, tf, future_tf):
    """Calculate the next key for a higher timeframe, except for tf == D1, W1, MN1 and except future_tf == W1, MN1"""
    if tf in ["D1", "W1", "MN1"] or future_tf in ["W1", "MN1"]: 
        return False

    _hour = key.hour
    _minute = key.minute
    if future_tf not in ["D1", "W1", "MN1"]:
        future_key = datetime.datetime.fromisoformat(key.strftime('%Y-%m-%d') + f" {key.hour:02d}:00")
    else:
        future_key = datetime.datetime.fromisoformat(key.strftime('%Y-%m-%d') + " 00:00")

    tfs = {'M1': 1, 'M2': 2, 'M5': 5, 'M10': 10, 'M15': 15, 'M30': 30, 'H1': 60, 'H2': 120, 'H4': 240, 'D1': 1440, 'W1': False, 'MN1': False}

    _k = tfs[tf]
    _k2 = tfs[future_tf]
    _i1 = _minute // _k2

    future_key = future_key + datetime.timedelta(minutes=_k2 * (_i1 + 1))
    future_key2 = future_key + datetime.timedelta(minutes=_k2 * (_i1 + 1))
    # print(key, "=>", future_key, "=>", future_key2, f"\t{tf} => {future_tf}")

    # print("\t", _hour, _minute, _k, _k2, _i1)
    return key, future_key, future_key2

def detect_class(key, future_key, future_key2, arr_OHLCV_1, timeframe_1, expected_change):
    """Determine the class to which the future candles at future_key, future_key2 belong"""
    if future_key in arr_OHLCV_1:
        _future_ohlcv = arr_OHLCV_1[future_key]
        # print(_future_ohlcv, "111111", key, "=>", future_key)
    else:
        # Search for the nearest future_key
        for k in list(arr_OHLCV_1.keys()):
            if k > key:
                future_key = k
                break
        _future_ohlcv = arr_OHLCV_1[future_key]
        # print(_future_ohlcv, "22222", key, "=>", future_key)

    # print(_future_ohlcv, "*******")
    _percent_OC = _future_ohlcv[5]  # 5 == _percent_OC
    _sign = math.copysign(1, _percent_OC)  # Get the sign of the percentage
    # print(_percent_OC, _sign)
    _classification_percent = _sign * get_classification(abs(_percent_OC), tf=timeframe_1, ex_ch=expected_change)

    if _classification_percent == 0:
        # Attempt to classify again by looking two candles ahead
        _pre_percent_OC = _percent_OC  # Consider % of the previous candle
        future_key = future_key2
        if future_key in arr_OHLCV_1:
            _future_ohlcv = arr_OHLCV_1[future_key]
            # print(_future_ohlcv, "33333", key, "=>", future_key)
        else:
            # Search for the nearest future_key
            for k in list(arr_OHLCV_1.keys()):
                if k > key:
                    future_key = k
                    break
            _future_ohlcv = arr_OHLCV_1[future_key]
            # print(_future_ohlcv, "44444", key, "=>", future_key)
        # print(_future_ohlcv, "**222**")
        _percent_OC = _future_ohlcv[5]  # 5 == _percent_OC
        _sign = math.copysign(1, _percent_OC)  # Get the sign of the percentage
        # print(_percent_OC, _sign)
        _percent_OC += _pre_percent_OC  # Consider % of the previous candle
        _classification_percent = _sign * get_classification(abs(_percent_OC), tf=timeframe_1, ex_ch=expected_change)

    return _classification_percent

def get_classification(_p, tf, ex_ch):
    """Determine the class based on the candle percentage"""
    _class_percent = 6
    for i in range(len(ex_ch[tf]) - 1):
        if ex_ch[tf][i] <= _p < ex_ch[tf][i + 1]:
            _class_percent = i
            break
    return _class_percent

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_error_and_exit(_error, _error_code):
    '''Function to print an error and stop the program'''
    print(bcolors.FAIL + _error + bcolors.ENDC)
    exit(_error_code)

def print_warning(_warning):
    '''Function to print a warning'''
    print(bcolors.WARNING + _warning + bcolors.ENDC)

def join_paths(paths):
    """Function to form a path from a list"""
    _folder = ''
    for _path in paths:
        _folder = os.path.join(_folder, _path)
    return _folder

def create_some_folders(timeframes, classes=None):
    """Function to create necessary directories"""
    folder = 'NN_winner'
    if not os.path.exists(folder): 
        os.makedirs(folder)

    folder = 'csv'
    if not os.path.exists(folder): 
        os.makedirs(folder)

    folder = 'NN'
    if not os.path.exists(folder): 
        os.makedirs(folder)

    for timeFrame in timeframes:
        _folder = os.path.join(folder, f"training_dataset_{timeFrame}")
        if not os.path.exists(_folder): 
            os.makedirs(_folder)

        if classes:
            for _class in classes:
                _folder_class = os.path.join(_folder, f"{_class}")
                if not os.path.exists(_folder_class): 
                    os.makedirs(_folder_class)

    _folder = os.path.join(folder, f"_data")
    if not os.path.exists(_folder): 
        os.makedirs(_folder)

    _folder = os.path.join(folder, f"_models")
    if not os.path.exists(_folder): 
        os.makedirs(_folder)

def start_redirect_output_from_screen_to_file(redirect, filename):
    '''Function to start redirecting output from the console to a file'''
    if redirect:
        sys.stdout = open(filename, 'w', encoding='utf8')

def stop_redirect_output_from_screen_to_file():
    '''Function to stop redirecting output from the console to a file'''
    try:
        sys.stdout.close()
    except:
        pass
