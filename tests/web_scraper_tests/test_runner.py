import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.web_scraper import WebScraper
from src.data.market_data import MarketData

class TestWebScraping(unittest.TestCase):
    def setUp(self):
        self.scraper = WebScraper()
        self.market_data = MarketData()
        
        # Sample mock data
        self.mock_stock_data = {
            'price': 150.00,
            'change': 2.5,
            'volume': 1000000,
            'market_cap': '2.5T',
            'pe_ratio': 25.5,
            '52w_high': 160.00,
            '52w_low': 140.00
        }
        
        self.mock_technical_data = {
            'rsi': 65,
            'macd': {
                'macd': 1.5,
                'signal': 1.0,
                'hist': 0.5
            },
            'sma': 148.5
        }

    @patch('src.data.web_scraper.WebScraper.get_stock_data')
    @patch('src.data.web_scraper.WebScraper.get_technical_indicators')
    def test_market_data_integration(self, mock_tech, mock_stock):
        """Test MarketData integration with WebScraper"""
        # Setup mock returns
        mock_stock.return_value = self.mock_stock_data
        mock_tech.return_value = self.mock_technical_data
        
        # Test stock analysis
        result = self.market_data.analyze_stock('AAPL')
        
        self.assertIsNotNone(result)
        self.assertIn('data', result)
        self.assertIn('technical_analysis', result)
        self.assertIn('price_analysis', result)
        self.assertIn('signals', result)
        
        # Verify data integration
        self.assertEqual(result['data']['price'], 150.00)
        self.assertEqual(result['data']['rsi'], 65)

    @patch('src.data.web_scraper.WebScraper.get_market_movers')
    @patch('src.data.web_scraper.WebScraper.get_market_news')
    @patch('src.data.web_scraper.WebScraper.get_stock_data')
    def test_market_overview(self, mock_stock, mock_news, mock_movers):
        """Test market overview functionality"""
        # Setup mock returns
        mock_movers.return_value = {
            'gainers': ['AAPL', 'GOOGL'],
            'losers': ['FB', 'TSLA']
        }
        mock_news.return_value = [
            {'title': 'Market Update 1', 'url': 'http://example.com/1'},
            {'title': 'Market Update 2', 'url': 'http://example.com/2'}
        ]
        mock_stock.return_value = self.mock_stock_data
        
        # Test market overview
        result = self.market_data.get_market_overview()
        
        self.assertIn('movers', result)
        self.assertIn('news', result)
        self.assertIn('indices', result)
        
        # Verify data integration
        self.assertEqual(len(result['movers']['gainers']), 2)
        self.assertEqual(len(result['news']), 2)

    @patch('src.data.web_scraper.WebScraper.get_stock_data')
    def test_error_handling(self, mock_stock):
        """Test error handling in market data integration"""
        # Test with None response
        mock_stock.return_value = None
        result = self.market_data.analyze_stock('INVALID')
        
        self.assertEqual(result, self.market_data._get_empty_analysis())
        
        # Test with network error
        mock_stock.side_effect = Exception("Network Error")
        result = self.market_data.analyze_stock('AAPL')
        
        self.assertEqual(result, self.market_data._get_empty_analysis())

    def test_technical_analysis(self):
        """Test technical analysis calculations"""
        # Test with sample data
        data = {**self.mock_stock_data, **self.mock_technical_data}
        
        analysis = self.market_data._analyze_technical_indicators(data)
        
        self.assertIn('trend', analysis)
        self.assertIn('strength', analysis)
        self.assertIn('signals', analysis)
        
        # Verify RSI signals
        self.assertIn('signals', analysis)
        if data['rsi'] > 70:
            self.assertIn('overbought', analysis['signals'])
        elif data['rsi'] < 30:
            self.assertIn('oversold', analysis['signals'])

    def test_price_analysis(self):
        """Test price action analysis"""
        analysis = self.market_data._analyze_price_action(self.mock_stock_data)
        
        self.assertIn('trend', analysis)
        self.assertIn('volatility', analysis)
        self.assertIn('support_resistance', analysis)
        
        # Verify trend calculation
        self.assertEqual(
            self.market_data._determine_trend({'change': 2.5}),
            'uptrend'
        )
        self.assertEqual(
            self.market_data._determine_trend({'change': -2.5}),
            'downtrend'
        )
        self.assertEqual(
            self.market_data._determine_trend({'change': 0.5}),
            'sideways'
        )

if __name__ == '__main__':
    unittest.main()
