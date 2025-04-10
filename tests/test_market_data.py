import unittest
from unittest.mock import patch, MagicMock
from src.data.market_data import MarketData

class TestMarketData(unittest.TestCase):
    def setUp(self):
        self.market_data = MarketData()
        
        # Sample data responses
        self.sample_stock_data = {
            'price': 150.00,
            'change': 2.5,
            'volume': 1000000,
            'market_cap': '2.5T',
            'pe_ratio': 25.5,
            '52w_high': 160.00,
            '52w_low': 140.00
        }
        
        self.sample_technical_data = {
            'rsi': 65,
            'macd': {
                'macd': 1.5,
                'signal': 1.0,
                'hist': 0.5
            },
            'sma': 148.5
        }
        
        self.sample_market_overview = {
            'movers': {
                'gainers': ['AAPL', 'GOOGL', 'MSFT'],
                'losers': ['FB', 'TSLA', 'NFLX']
            },
            'news': [
                {'title': 'Market Update 1', 'url': 'http://example.com/1'},
                {'title': 'Market Update 2', 'url': 'http://example.com/2'}
            ]
        }

    @patch('src.data.web_scraper.WebScraper')
    def test_get_stock_data(self, mock_scraper):
        """Test getting comprehensive stock data"""
        # Mock scraper responses
        mock_instance = mock_scraper.return_value
        mock_instance.get_stock_data.return_value = self.sample_stock_data
        mock_instance.get_technical_indicators.return_value = self.sample_technical_data
        
        result = self.market_data.get_stock_data("AAPL")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['price'], 150.00)
        self.assertEqual(result['change'], 2.5)
        self.assertEqual(result['volume'], 1000000)
        self.assertEqual(result['rsi'], 65)
        self.assertEqual(result['macd']['macd'], 1.5)
        
        # Test error handling
        mock_instance.get_stock_data.return_value = None
        result = self.market_data.get_stock_data("INVALID")
        self.assertIsNone(result)

    @patch('src.data.web_scraper.WebScraper')
    def test_get_market_overview(self, mock_scraper):
        """Test getting market overview"""
        # Mock scraper responses
        mock_instance = mock_scraper.return_value
        mock_instance.get_market_movers.return_value = self.sample_market_overview['movers']
        mock_instance.get_market_news.return_value = self.sample_market_overview['news']
        mock_instance.get_stock_data.return_value = self.sample_stock_data
        
        result = self.market_data.get_market_overview()
        
        self.assertIn('movers', result)
        self.assertIn('news', result)
        self.assertIn('indices', result)
        self.assertEqual(len(result['movers']['gainers']), 3)
        self.assertEqual(len(result['movers']['losers']), 3)
        self.assertEqual(len(result['news']), 2)
        
        # Test error handling
        mock_instance.get_market_movers.side_effect = Exception("Error")
        result = self.market_data.get_market_overview()
        self.assertEqual(len(result['movers']['gainers']), 0)

    @patch('src.data.web_scraper.WebScraper')
    def test_analyze_stock(self, mock_scraper):
        """Test stock analysis"""
        # Mock scraper responses
        mock_instance = mock_scraper.return_value
        mock_instance.get_stock_data.return_value = self.sample_stock_data
        mock_instance.get_technical_indicators.return_value = self.sample_technical_data
        
        result = self.market_data.analyze_stock("AAPL")
        
        self.assertIn('data', result)
        self.assertIn('technical_analysis', result)
        self.assertIn('price_analysis', result)
        self.assertIn('signals', result)
        
        # Verify technical analysis
        tech_analysis = result['technical_analysis']
        self.assertIn('trend', tech_analysis)
        self.assertIn('strength', tech_analysis)
        self.assertIn('signals', tech_analysis)
        
        # Verify price analysis
        price_analysis = result['price_analysis']
        self.assertIn('trend', price_analysis)
        self.assertIn('volatility', price_analysis)
        self.assertIn('support_resistance', price_analysis)
        
        # Test error handling
        mock_instance.get_stock_data.return_value = None
        result = self.market_data.analyze_stock("INVALID")
        self.assertEqual(result, self.market_data._get_empty_analysis())

    def test_technical_analysis(self):
        """Test technical analysis calculations"""
        data = {**self.sample_stock_data, **self.sample_technical_data}
        
        analysis = self.market_data._analyze_technical_indicators(data)
        
        self.assertIn('trend', analysis)
        self.assertIn('strength', analysis)
        self.assertIn('signals', analysis)
        self.assertIsInstance(analysis['signals'], list)

    def test_price_analysis(self):
        """Test price action analysis"""
        data = self.sample_stock_data.copy()
        
        analysis = self.market_data._analyze_price_action(data)
        
        self.assertIn('trend', analysis)
        self.assertIn('volatility', analysis)
        self.assertIn('support_resistance', analysis)
        
        # Test trend determination
        self.assertEqual(self.market_data._determine_trend({'change': 2.5}), 'uptrend')
        self.assertEqual(self.market_data._determine_trend({'change': -2.5}), 'downtrend')
        self.assertEqual(self.market_data._determine_trend({'change': 0.5}), 'sideways')
        
        # Test volatility calculation
        self.assertEqual(
            self.market_data._calculate_volatility({
                '52w_high': 200,
                '52w_low': 100
            }),
            'high'
        )

    def test_signal_generation(self):
        """Test trading signal generation"""
        technical_analysis = {
            'trend': 'uptrend',
            'strength': 'strong',
            'signals': ['bullish_macd', 'oversold']
        }
        
        price_analysis = {
            'trend': 'uptrend',
            'volatility': 'high'
        }
        
        signals = self.market_data._generate_signals(technical_analysis, price_analysis)
        
        self.assertIsInstance(signals, list)
        self.assertIn('bullish_macd', signals)
        self.assertIn('oversold', signals)
        self.assertIn('trend_following_buy', signals)
        self.assertIn('high_volatility', signals)

if __name__ == '__main__':
    unittest.main()
