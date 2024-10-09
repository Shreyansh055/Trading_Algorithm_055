# Configuration file for the trading strategy

class Config:
    """Class to hold configuration settings for the trading strategy."""
    
    # Tickers for training the neural network
    training_NN = {"SBER", "VTBR"}  # Stocks used for training the neural network
    
    # Tickers for trading and downloading historical data
    portfolio = {"SBER", "VTBR"}  # Stocks for trading and historical data retrieval
    
    # Security board class
    security_board = "TQBR"  # Class of tickers

    # Available timeframes: M1, M10, H1
    timeframe_0 = "M1"  # Timeframe for training the neural network (entry)
    timeframe_1 = "M10"  # Timeframe for training the neural network (exit)
    
    # Start date for downloading historical data from MOEX
    start = "2021-01-01"

    # Trading hours for the exchange
    trading_hours_start = "10:00"  # Start time of the trading session
    trading_hours_end = "23:50"  # End time of the trading session

    # Parameters for visualizing data
    period_sma_slow = 64  # Period for slow Simple Moving Average (SMA)
    period_sma_fast = 16  # Period for fast Simple Moving Average (SMA)
    draw_window = 128  # Size of the data window for drawing
    steps_skip = 16  # Step size for shifting the data window
    draw_size = 128  # Size of the square image side

# Example usage of the Config class
if __name__ == "__main__":
    # Printing configuration settings
    print("Training Tickers:", Config.training_NN)
    print("Trading Portfolio:", Config.portfolio)
    print("Security Board:", Config.security_board)
    print("Trading Hours:", Config.trading_hours_start, "to", Config.trading_hours_end)
