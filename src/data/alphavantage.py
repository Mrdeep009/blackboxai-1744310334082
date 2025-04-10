import requests
from typing import Dict, List, Optional
from ..utils.logger import get_logger, log_api_call
from .api_key_manager import APIKeyManager

class AlphaVantageAPI:
    def __init__(self, initial_api_key: str = None):
        """
        Initialize AlphaVantage API client
        
        Args:
            initial_api_key (str, optional): Initial API key to use
        """
        self.base_url = "https://www.alphavantage.co/query"
        self.logger = get_logger(__name__)
        self.key_manager = APIKeyManager()
        if initial_api_key:
            self.key_manager.keys.append(initial_api_key)
            self.key_manager.key_usage[initial_api_key] = {
                'count': 0,
                'last_used': None,
                'daily_limit': 25,
                'minute_limit': 5
            }

    def _get_api_key(self) -> str:
        """
        Get a valid API key
        
        Returns:
            str: API key to use
        """
        return self.key_manager.get_api_key()

    @log_api_call
    def get_quote_data(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote data for a symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Quote data or None if request fails
        """
        try:
            api_key = self._get_api_key()
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "5min",
                "apikey": api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            # Check for error responses
            if "Error Message" in data:
                self.logger.error(f"Invalid response for {symbol}: {data}")
                return None
                
            if "Note" in data:
                self.key_manager.report_error(api_key, str(data["Note"]))
                return self.get_quote_data(symbol)  # Retry with new key
                
            if "Information" in data:
                self.key_manager.report_error(api_key, str(data["Information"]))
                return self.get_quote_data(symbol)  # Retry with new key
                
            time_series = data.get("Time Series (5min)")
            if not time_series:
                self.logger.error(f"Invalid response for {symbol}: {data}")
                return None
                
            # Extract latest data point
            latest_time = list(time_series.keys())[0]
            latest_data = time_series[latest_time]
            
            # Extract historical data
            prices = self._extract_prices(time_series)
            volumes = self._extract_volumes(time_series)
            
            return {
                "price": float(latest_data["4. close"]),
                "volume": int(latest_data["5. volume"]),
                "change": self._calculate_daily_change(time_series),
                "prices": prices,
                "volumes": volumes
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching quote data for {symbol}: {str(e)}")
            return None

    @log_api_call
    def get_market_data(self) -> Dict:
        """
        Get market-wide data
        
        Returns:
            Dict: Market data for multiple symbols
        """
        try:
            # Get list of symbols
            symbols = self.get_all_symbols()
            market_data = {}
            
            # Get data for each symbol
            for symbol in symbols:
                quote_data = self.get_quote_data(symbol)
                if quote_data:
                    market_data[symbol] = quote_data
                    
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return {}

    @log_api_call
    def get_all_symbols(self) -> List[str]:
        """
        Get list of all available symbols
        
        Returns:
            List[str]: List of stock symbols
        """
        try:
            api_key = self._get_api_key()
            params = {
                "function": "TOP_GAINERS_LOSERS",
                "apikey": api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Note" in data or "Information" in data:
                self.key_manager.report_error(api_key, str(data))
                return self.get_all_symbols()  # Retry with new key
            
            symbols = []
            
            # Extract symbols from gainers and losers
            for category in ["top_gainers", "top_losers"]:
                if category in data:
                    symbols.extend([item["ticker"] for item in data[category]])
                    
            return list(set(symbols))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error fetching symbols: {str(e)}")
            return []

    @log_api_call
    def get_technical_indicators(self, symbol: str) -> Optional[Dict]:
        """
        Get technical indicators for a symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Technical indicators or None if request fails
        """
        try:
            # Get RSI
            rsi = self._get_rsi(symbol)
            
            # Get MACD
            macd = self._get_macd(symbol)
            
            # Get SMA
            sma = self._get_sma(symbol)
            
            # Return None if all indicators failed
            if rsi is None and macd is None and sma is None:
                return None
                
            return {
                "rsi": rsi,
                "macd": macd,
                "sma": sma
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching technical indicators: {str(e)}")
            return None

    def _get_rsi(self, symbol: str) -> Optional[float]:
        """
        Get RSI value
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[float]: RSI value
        """
        try:
            api_key = self._get_api_key()
            params = {
                "function": "RSI",
                "symbol": symbol,
                "interval": "daily",
                "time_period": 14,
                "series_type": "close",
                "apikey": api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Note" in data or "Information" in data:
                self.key_manager.report_error(api_key, str(data))
                return self._get_rsi(symbol)  # Retry with new key
            
            if "Technical Analysis: RSI" not in data:
                self.logger.error(f"Error fetching RSI for {symbol}: {data}")
                return None
                
            latest_date = list(data["Technical Analysis: RSI"].keys())[0]
            return float(data["Technical Analysis: RSI"][latest_date]["RSI"])
            
        except Exception as e:
            self.logger.error(f"Error fetching RSI for {symbol}: {str(e)}")
            return None

    def _get_macd(self, symbol: str) -> Optional[Dict]:
        """
        Get MACD values
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: MACD values
        """
        try:
            api_key = self._get_api_key()
            params = {
                "function": "MACD",
                "symbol": symbol,
                "interval": "daily",
                "series_type": "close",
                "apikey": api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Note" in data or "Information" in data:
                self.key_manager.report_error(api_key, str(data))
                return self._get_macd(symbol)  # Retry with new key
            
            if "Technical Analysis: MACD" not in data:
                self.logger.error(f"Error fetching MACD for {symbol}: {data}")
                return None
                
            latest_date = list(data["Technical Analysis: MACD"].keys())[0]
            latest_data = data["Technical Analysis: MACD"][latest_date]
            
            return {
                "macd": float(latest_data["MACD"]),
                "signal": float(latest_data["MACD_Signal"]),
                "hist": float(latest_data["MACD_Hist"])
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching MACD for {symbol}: {str(e)}")
            return None

    def _get_sma(self, symbol: str) -> Optional[float]:
        """
        Get SMA value
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[float]: SMA value
        """
        try:
            api_key = self._get_api_key()
            params = {
                "function": "SMA",
                "symbol": symbol,
                "interval": "daily",
                "time_period": 20,
                "series_type": "close",
                "apikey": api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Note" in data or "Information" in data:
                self.key_manager.report_error(api_key, str(data))
                return self._get_sma(symbol)  # Retry with new key
            
            if "Technical Analysis: SMA" not in data:
                return None
                
            latest_date = list(data["Technical Analysis: SMA"].keys())[0]
            return float(data["Technical Analysis: SMA"][latest_date]["SMA"])
            
        except Exception as e:
            self.logger.error(f"Error fetching SMA for {symbol}: {str(e)}")
            return None

    def _extract_prices(self, time_series: Dict) -> List[float]:
        """
        Extract closing prices from time series data
        
        Args:
            time_series (Dict): Time series data
            
        Returns:
            List[float]: List of prices
        """
        try:
            return [float(data["4. close"]) for data in time_series.values()]
        except Exception:
            return []

    def _extract_volumes(self, time_series: Dict) -> List[int]:
        """
        Extract volumes from time series data
        
        Args:
            time_series (Dict): Time series data
            
        Returns:
            List[int]: List of volumes
        """
        try:
            return [int(data["5. volume"]) for data in time_series.values()]
        except Exception:
            return []

    def _calculate_daily_change(self, time_series: Dict) -> float:
        """
        Calculate daily percentage change
        
        Args:
            time_series (Dict): Time series data
            
        Returns:
            float: Percentage change
        """
        try:
            if not time_series:
                return 0.0
                
            prices = [float(data["4. close"]) for data in time_series.values()]
            if len(prices) < 2:
                return 0.0
                
            return ((prices[0] - prices[1]) / prices[1]) * 100
            
        except Exception:
            return 0.0
