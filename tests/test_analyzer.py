import unittest
from unittest.mock import Mock, patch
from src.core.analyzer import TradeAnalyzer
from src.data.market_data import MarketData

class TestTradeAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.config = {
            'RSI_OVERBOUGHT': 70,
            'RSI_OVERSOLD': 30,
            'SCAN_INTERVAL': 5
        }
        self.analyzer = TradeAnalyzer(self.config)

    @patch('src.data.market_data.MarketData')
    def test_analyze_quote(self, mock_market_data):
        """Test quote analysis"""
        # Mock market data response
        mock_market_data.return_value.analyze_stock.return_value = {
            'data': {
                'price': 150.0,
                'change': 2.5,
                'volume': 1000000,
                'rsi': 65,
                'macd': {'macd': 1.5, 'signal': 1.0}
            },
            'technical_analysis': {
                'trend': 'uptrend',
                'strength': 'strong',
                'signals': ['bullish_macd']
            },
            'price_analysis': {
                'trend': 'uptrend',
                'volatility': 'medium'
            },
            'signals': ['bullish_macd', 'trend_following_buy']
        }

        # Test analysis
        result = self.analyzer.analyze_quote('AAPL')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['price'], 150.0)
        self.assertEqual(result['change'], 2.5)
        self.assertEqual(result['volume'], 1000000)
        self.assertEqual(result['rsi'], 65)
        self.assertEqual(result['macd'], 1.5)

    @patch('src.data.market_data.MarketData')
    def test_get_top_recommendations(self, mock_market_data):
        """Test getting top recommendations"""
        # Mock market data response
        mock_market_data.return_value.get_market_overview.return_value = {
            'movers': {
                'gainers': ['AAPL', 'GOOGL', 'MSFT'],
                'losers': ['FB', 'TSLA', 'NFLX']
            }
        }
        
        mock_market_data.return_value.analyze_stock.return_value = {
            'data': {
                'price': 150.0,
                'change': 2.5,
                'volume': 1000000
            },
            'technical_analysis': {
                'trend': 'uptrend',
                'strength': 'strong',
                'signals': ['bullish_macd']
            },
            'price_analysis': {
                'trend': 'uptrend',
                'volatility': 'medium'
            },
            'signals': ['bullish_macd']
        }

        # Test recommendations
        recommendations = self.analyzer.get_top_recommendations()
        
        self.assertEqual(len(recommendations), 6)
        self.assertIn('symbol', recommendations[0])
        self.assertIn('action', recommendations[0])
        self.assertIn('win_rate', recommendations[0])
        self.assertIn('risk', recommendations[0])

    @patch('src.data.market_data.MarketData')
    def test_analyze_all_quotes(self, mock_market_data):
        """Test analyzing all quotes"""
        # Mock market data response
        mock_market_data.return_value.get_market_overview.return_value = {
            'movers': {
                'gainers': ['AAPL', 'GOOGL'],
                'losers': ['FB', 'TSLA']
            }
        }
        
        mock_market_data.return_value.analyze_stock.return_value = {
            'data': {
                'price': 150.0,
                'change': 2.5,
                'volume': 1000000
            },
            'technical_analysis': {
                'trend': 'uptrend',
                'strength': 'strong',
                'signals': ['bullish_macd']
            },
            'price_analysis': {
                'trend': 'uptrend',
                'volatility': 'medium'
            },
            'signals': ['bullish_macd']
        }

        # Test analysis of all quotes
        results = self.analyzer.analyze_all_quotes()
        
        self.assertEqual(len(results), 4)
        self.assertIn('symbol', results[0])
        self.assertIn('action', results[0])
        self.assertIn('win_rate', results[0])
        self.assertIn('risk', results[0])

    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid symbol
        result = self.analyzer.analyze_quote(None)
        self.assertIsNone(result)

        # Test with empty data
        result = self.analyzer.analyze_quote('')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
