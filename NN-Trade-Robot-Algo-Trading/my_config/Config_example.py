class Config:
    """Configuration class for accessing the trading API."""
    
    # Trading account IDs
    ClientIds = ('<Your_Trading_Account>',)  # Replace with your trading account ID(s)
    
    # Access token for authentication
    AccessToken = '<Your_Access_Token>'  # Replace with your access token

    @staticmethod
    def display_config():
        """Print the current configuration settings."""
        print("Trading Account IDs:", Config.ClientIds)
        print("Access Token:", Config.AccessToken)