import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '4WK9X5Q7BWLBTVZM')
    
    # Analysis Parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    # Scanning Parameters
    SCAN_INTERVAL = 5  # seconds for single quote
    BULK_SCAN_INTERVAL = 25  # seconds for analyzing all quotes
    MAX_RECOMMENDATIONS = 6
    
    # Risk Management
    DEFAULT_RISK_PERCENTAGE = 2  # Default risk per trade
    DEFAULT_POSITION_SIZE = 1000  # Default position size
    
    # Technical Analysis Weights
    WEIGHTS = {
        'technical': {
            'rsi': 0.10,
            'macd': 0.10,
            'moving_averages': 0.10,
            'volume': 0.10
        },
        'patterns': {
            'recognition': 0.15,
            'trend_strength': 0.15
        },
        'sentiment': {
            'news': 0.10,
            'social': 0.10,
            'market': 0.10
        }
    }
    
    # Data Sources
    DATA_SOURCES = [
        'alphavantage',
        'yahoo_finance',
        'finviz',
        'stocktwits'
    ]

def load_config():
    """
    Load and return configuration settings
    """
    return Config()
