import unittest
import numpy as np
from src.indicators.rsi import RSIIndicator
from src.indicators.macd import MACDIndicator
from src.indicators.volume import VolumeAnalyzer

class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.rsi = RSIIndicator(period=14)
        self.macd = MACDIndicator(12, 26, 9)
        self.volume = VolumeAnalyzer()
        
        # Sample data for testing
        self.sample_prices = [
            100.0, 102.0, 104.0, 103.0, 105.0, 107.0, 108.0, 107.0, 106.0, 105.0,
            104.0, 103.0, 102.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0,
            108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0,
            118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0, 125.0, 126.0, 127.0
        ]
        
        self.sample_volumes = [
            1000, 1200, 1100, 900, 1300, 1500, 1400, 1200, 1100, 1000,
            900, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600,
            1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600,
            2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600
        ]

    def test_rsi_calculation(self):
        """Test RSI calculation"""
        rsi = self.rsi.calculate(self.sample_prices)
        
        # RSI should be between 0 and 100
        self.assertIsNotNone(rsi)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
        
        # Test with insufficient data
        rsi_short = self.rsi.calculate(self.sample_prices[:5])
        self.assertIsNone(rsi_short)

    def test_macd_calculation(self):
        """Test MACD calculation"""
        macd, signal, hist = self.macd.calculate(self.sample_prices)
        
        # Check if values are calculated
        self.assertIsNotNone(macd)
        self.assertIsNotNone(signal)
        self.assertIsNotNone(hist)
        
        # Test MACD signal generation
        signal_str = self.macd.get_signal(macd, signal, hist)
        self.assertIn(signal_str, ['strong_buy', 'buy', 'strong_sell', 'sell', 'neutral'])
        
        # Test with insufficient data
        macd_short = self.macd.calculate(self.sample_prices[:5])
        self.assertEqual(macd_short, (None, None, None))

    def test_volume_analysis(self):
        """Test volume analysis"""
        volume_data = self.volume.analyze_volume(
            self.sample_prices,
            self.sample_volumes
        )
        
        # Check if all expected keys are present
        expected_keys = [
            'average_volume',
            'volume_trend',
            'price_volume_correlation',
            'unusual_volume',
            'volume_signal'
        ]
        
        for key in expected_keys:
            self.assertIn(key, volume_data)
        
        # Test volume trend
        self.assertIn(
            volume_data['volume_trend'],
            ['increasing', 'decreasing', 'neutral']
        )
        
        # Test volume signal
        self.assertIn(
            volume_data['volume_signal'],
            ['strong_volume', 'weak_volume', 'unusual_volume', 'normal_volume']
        )

    def test_volume_strength(self):
        """Test volume strength calculation"""
        volume_data = self.volume.analyze_volume(
            self.sample_prices,
            self.sample_volumes
        )
        
        strength = self.volume.get_volume_strength(volume_data)
        self.assertIn(strength, ['strong', 'weak', 'unusual', 'normal'])

    def test_trend_confirmation(self):
        """Test volume trend confirmation"""
        volume_data = self.volume.analyze_volume(
            self.sample_prices,
            self.sample_volumes
        )
        
        # Test uptrend confirmation
        is_confirmed = self.volume.is_volume_confirming_trend(
            'uptrend',
            volume_data
        )
        self.assertIsInstance(is_confirmed, bool)
        
        # Test downtrend confirmation
        is_confirmed = self.volume.is_volume_confirming_trend(
            'downtrend',
            volume_data
        )
        self.assertIsInstance(is_confirmed, bool)

    def test_edge_cases(self):
        """Test edge cases for all indicators"""
        # Empty data
        self.assertIsNone(self.rsi.calculate([]))
        self.assertEqual(self.macd.calculate([]), (None, None, None))
        self.assertEqual(
            self.volume.analyze_volume([], []),
            {
                "average_volume": 0,
                "volume_trend": "neutral",
                "price_volume_correlation": 0,
                "unusual_volume": False,
                "volume_signal": "normal_volume"
            }
        )
        
        # Single value
        self.assertIsNone(self.rsi.calculate([100]))
        self.assertEqual(self.macd.calculate([100]), (None, None, None))
        self.assertEqual(
            self.volume.analyze_volume([100], [1000]),
            {
                "average_volume": 0,
                "volume_trend": "neutral",
                "price_volume_correlation": 0,
                "unusual_volume": False,
                "volume_signal": "normal_volume"
            }
        )
        
        # None values
        self.assertIsNone(self.rsi.calculate(None))
        self.assertEqual(self.macd.calculate(None), (None, None, None))
        self.assertEqual(
            self.volume.analyze_volume(None, None),
            {
                "average_volume": 0,
                "volume_trend": "neutral",
                "price_volume_correlation": 0,
                "unusual_volume": False,
                "volume_signal": "normal_volume"
            }
        )

    def test_indicator_combinations(self):
        """Test combined indicator signals"""
        # Calculate all indicators
        rsi = self.rsi.calculate(self.sample_prices)
        macd, signal, hist = self.macd.calculate(self.sample_prices)
        volume_data = self.volume.analyze_volume(
            self.sample_prices,
            self.sample_volumes
        )
        
        # Verify RSI and MACD combination
        if rsi is not None and macd is not None:
            # RSI overbought (>70) and MACD bearish should indicate strong sell
            if rsi > 70 and macd < signal:
                macd_signal = self.macd.get_signal(macd, signal, hist)
                self.assertEqual(macd_signal, 'strong_sell')
            
            # RSI oversold (<30) and MACD bullish should indicate strong buy
            if rsi < 30 and macd > signal:
                macd_signal = self.macd.get_signal(macd, signal, hist)
                self.assertEqual(macd_signal, 'strong_buy')
        
        # Verify volume confirmation
        if volume_data['volume_signal'] == 'strong_volume':
            self.assertIn(
                volume_data['volume_trend'],
                ['increasing', 'decreasing']
            )

if __name__ == '__main__':
    unittest.main()
