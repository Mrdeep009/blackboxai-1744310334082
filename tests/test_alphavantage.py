import unittest
from unittest.mock import patch, MagicMock
from src.data.alphavantage import AlphaVantageAPI

class TestAlphaVantageAPI(unittest.TestCase):
    def setUp(self):
        self.api = AlphaVantageAPI("test_api_key")
        
        # Sample API responses
        self.sample_intraday_response = {
            "Time Series (5min)": {
                "2023-01-01 12:00:00": {
                    "1. open": "100.0000",
                    "2. high": "101.0000",
                    "3. low": "99.0000",
                    "4. close": "100.5000",
                    "5. volume": "1000000"
                }
            }
        }
        
        self.sample_daily_response = {
            "Time Series (Daily)": {
                "2023-01-01": {
                    "1. open": "100.0000",
                    "2. high": "101.0000",
                    "3. low": "99.0000",
                    "4. close": "100.5000",
                    "5. volume": "1000000"
                }
            }
        }
        
        self.sample_technical_response = {
            "Technical Analysis: RSI": {
                "2023-01-01": {
                    "RSI": "55.0000"
                }
            }
        }

    @patch('requests.get')
    def test_get_quote_data(self, mock_get):
        """Test getting quote data"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_intraday_response
        mock_get.return_value = mock_response
        
        result = self.api.get_quote_data("AAPL")
        
        self.assertIsNotNone(result)
        self.assertIn('price', result)
        self.assertIn('volume', result)
        self.assertIn('change', result)
        self.assertIn('prices', result)
        self.assertIn('volumes', result)
        
        # Test error handling
        mock_response.json.return_value = {"Error Message": "Invalid API call"}
        result = self.api.get_quote_data("INVALID")
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_market_data(self, mock_get):
        """Test getting market data"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.side_effect = [
            {"top_gainers": [{"ticker": "AAPL"}, {"ticker": "GOOGL"}]},
            self.sample_intraday_response,
            self.sample_intraday_response
        ]
        mock_get.return_value = mock_response
        
        result = self.api.get_market_data()
        
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)
        
        # Test error handling
        mock_response.json.side_effect = Exception("API Error")
        result = self.api.get_market_data()
        self.assertEqual(len(result), 0)

    @patch('requests.get')
    def test_get_all_symbols(self, mock_get):
        """Test getting all symbols"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "top_gainers": [{"ticker": "AAPL"}, {"ticker": "GOOGL"}],
            "top_losers": [{"ticker": "FB"}, {"ticker": "TSLA"}]
        }
        mock_get.return_value = mock_response
        
        result = self.api.get_all_symbols()
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(set(result)), len(result))  # Check for duplicates
        
        # Test error handling
        mock_response.json.side_effect = Exception("API Error")
        result = self.api.get_all_symbols()
        self.assertEqual(len(result), 0)

    @patch('requests.get')
    def test_get_technical_indicators(self, mock_get):
        """Test getting technical indicators"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_technical_response
        mock_get.return_value = mock_response
        
        result = self.api.get_technical_indicators("AAPL")
        
        self.assertIsNotNone(result)
        self.assertIn('rsi', result)
        self.assertIn('macd', result)
        self.assertIn('sma', result)
        
        # Test error handling
        mock_response.json.side_effect = Exception("API Error")
        result = self.api.get_technical_indicators("AAPL")
        self.assertIsNone(result)

    @patch('requests.get')
    def test_rate_limiting(self, mock_get):
        """Test API rate limiting handling"""
        # Mock rate limit response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Note": "Thank you for using Alpha Vantage! Our standard API rate limit is 5 calls per minute."
        }
        mock_get.return_value = mock_response
        
        result = self.api.get_quote_data("AAPL")
        self.assertIsNone(result)

    def test_data_extraction(self):
        """Test data extraction methods"""
        # Test price extraction
        prices = self.api._extract_prices({
            "2023-01-01": {"4. close": "100.50"},
            "2023-01-02": {"4. close": "101.50"}
        })
        self.assertEqual(len(prices), 2)
        self.assertEqual(prices[0], 100.50)
        
        # Test volume extraction
        volumes = self.api._extract_volumes({
            "2023-01-01": {"5. volume": "1000"},
            "2023-01-02": {"5. volume": "2000"}
        })
        self.assertEqual(len(volumes), 2)
        self.assertEqual(volumes[0], 1000)

    def test_daily_change_calculation(self):
        """Test daily change calculation"""
        daily_data = {
            "2023-01-02": {"4. close": "101.00"},
            "2023-01-01": {"4. close": "100.00"}
        }
        
        change = self.api._calculate_daily_change(daily_data)
        self.assertEqual(change, 1.0)  # 1% increase
        
        # Test with invalid data
        self.assertEqual(self.api._calculate_daily_change(None), 0.0)
        self.assertEqual(self.api._calculate_daily_change({}), 0.0)

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """Test various error handling scenarios"""
        # Test network error
        mock_get.side_effect = Exception("Network Error")
        result = self.api.get_quote_data("AAPL")
        self.assertIsNone(result)
        
        # Test invalid JSON response
        mock_get.side_effect = None
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        result = self.api.get_quote_data("AAPL")
        self.assertIsNone(result)
        
        # Test missing data in response
        mock_response.json.side_effect = None
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        result = self.api.get_quote_data("AAPL")
        self.assertIsNone(result)

    @patch('requests.get')
    def test_api_parameters(self, mock_get):
        """Test API call parameters"""
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_intraday_response
        mock_get.return_value = mock_response
        
        self.api.get_quote_data("AAPL")
        
        # Verify API call parameters
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['apikey'], "test_api_key")
        self.assertEqual(kwargs['params']['symbol'], "AAPL")
        self.assertIn('function', kwargs['params'])

if __name__ == '__main__':
    unittest.main()
