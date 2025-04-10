import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from src.data.web_scraper import WebScraper

class TestWebScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = WebScraper()
        
        # Sample HTML responses
        self.sample_yahoo_html = """
        <html>
            <fin-streamer data-symbol="AAPL" data-field="regularMarketPrice" value="150.00"></fin-streamer>
            <fin-streamer data-symbol="AAPL" data-field="regularMarketChangePercent" value="2.5"></fin-streamer>
            <fin-streamer data-symbol="AAPL" data-field="regularMarketVolume" value="1000000"></fin-streamer>
            <td>52 Week Range</td>
            <td>140.00 - 160.00</td>
        </html>
        """
        
        self.sample_marketwatch_html = """
        <html>
            <div>Market Cap</div>
            <div>2.5T</div>
            <div>P/E Ratio</div>
            <div>25.5</div>
        </html>
        """
        
        self.sample_movers_html = """
        <html>
            <table class="W(100%)">
                <tr><a>AAPL</a></tr>
                <tr><a>GOOGL</a></tr>
            </table>
        </html>
        """
        
        self.sample_news_html = """
        <html>
            <h3><a href="/news/article1">Market Update 1</a></h3>
            <h3><a href="/news/article2">Market Update 2</a></h3>
        </html>
        """

    @patch('requests.get')
    def test_get_stock_data(self, mock_get):
        """Test getting stock data"""
        # Mock responses
        mock_yahoo = MagicMock()
        mock_yahoo.text = self.sample_yahoo_html
        mock_marketwatch = MagicMock()
        mock_marketwatch.text = self.sample_marketwatch_html
        
        mock_get.side_effect = [mock_yahoo, mock_marketwatch]
        
        result = self.scraper.get_stock_data("AAPL")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['price'], 150.00)
        self.assertEqual(result['change'], 2.5)
        self.assertEqual(result['volume'], 1000000)
        self.assertEqual(result['market_cap'], "2.5T")
        self.assertEqual(result['pe_ratio'], 25.5)
        
        # Test error handling
        mock_get.side_effect = Exception("Network Error")
        result = self.scraper.get_stock_data("AAPL")
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_market_movers(self, mock_get):
        """Test getting market movers"""
        # Mock responses
        mock_response = MagicMock()
        mock_response.text = self.sample_movers_html
        mock_get.return_value = mock_response
        
        result = self.scraper.get_market_movers()
        
        self.assertIn('gainers', result)
        self.assertIn('losers', result)
        self.assertGreater(len(result['gainers']), 0)
        self.assertGreater(len(result['losers']), 0)
        
        # Test error handling
        mock_get.side_effect = Exception("Network Error")
        result = self.scraper.get_market_movers()
        self.assertEqual(len(result['gainers']), 0)
        self.assertEqual(len(result['losers']), 0)

    @patch('requests.get')
    def test_get_market_news(self, mock_get):
        """Test getting market news"""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = self.sample_news_html
        mock_get.return_value = mock_response
        
        result = self.scraper.get_market_news()
        
        self.assertGreater(len(result), 0)
        self.assertIn('title', result[0])
        self.assertIn('url', result[0])
        
        # Test error handling
        mock_get.side_effect = Exception("Network Error")
        result = self.scraper.get_market_news()
        self.assertEqual(len(result), 0)

    @patch('requests.get')
    def test_get_technical_indicators(self, mock_get):
        """Test getting technical indicators"""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = self.sample_yahoo_html
        mock_get.return_value = mock_response
        
        result = self.scraper.get_technical_indicators("AAPL")
        
        self.assertIsNotNone(result)
        self.assertIn('rsi', result)
        self.assertIn('macd', result)
        self.assertIn('sma', result)
        
        # Test error handling
        mock_get.side_effect = Exception("Network Error")
        result = self.scraper.get_technical_indicators("AAPL")
        self.assertIsNone(result)

    def test_random_delay(self):
        """Test random delay generation"""
        delay = self.scraper._get_random_delay()
        self.assertGreaterEqual(delay, self.scraper.min_delay)
        self.assertLessEqual(delay, self.scraper.max_delay)

    def test_calculate_technical_indicators(self):
        """Test technical indicator calculations"""
        prices = [100, 102, 98, 103, 97, 105]
        
        # Test RSI calculation
        rsi = self.scraper._calculate_rsi(prices)
        self.assertIsNotNone(rsi)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
        
        # Test MACD calculation
        macd, signal, hist = self.scraper._calculate_macd(prices)
        self.assertIsNotNone(macd)
        self.assertIsNotNone(signal)
        self.assertIsNotNone(hist)
        
        # Test SMA calculation
        sma = self.scraper._calculate_sma(prices)
        self.assertIsNotNone(sma)
        
        # Test with insufficient data
        self.assertIsNone(self.scraper._calculate_rsi([100]))
        self.assertEqual(self.scraper._calculate_macd([100]), (None, None, None))
        self.assertIsNone(self.scraper._calculate_sma([100]))

if __name__ == '__main__':
    unittest.main()
