import unittest
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from src.utils.helpers import (
    calculate_percentage_change,
    calculate_risk_reward_ratio,
    calculate_position_size,
    format_price,
    calculate_moving_average,
    calculate_volatility,
    format_timestamp,
    calculate_win_rate,
    normalize_data,
    calculate_correlation,
    format_percentage,
    calculate_drawdown
)
from src.utils.logger import setup_logger, get_logger, LoggerMixin, log_execution_time, cleanup_logs

class TestHelpers(unittest.TestCase):
    def test_calculate_percentage_change(self):
        """Test percentage change calculation"""
        self.assertEqual(calculate_percentage_change(110, 100), 10.0)
        self.assertEqual(calculate_percentage_change(90, 100), -10.0)
        self.assertEqual(calculate_percentage_change(100, 100), 0.0)
        self.assertEqual(calculate_percentage_change(100, 0), 0.0)  # Edge case

    def test_calculate_risk_reward_ratio(self):
        """Test risk/reward ratio calculation"""
        self.assertEqual(calculate_risk_reward_ratio(100, 90, 120), 2.0)
        self.assertEqual(calculate_risk_reward_ratio(100, 100, 120), 0.0)  # Edge case
        self.assertEqual(calculate_risk_reward_ratio(100, 90, 100), 0.0)  # Edge case

    def test_calculate_position_size(self):
        """Test position size calculation"""
        self.assertEqual(calculate_position_size(10000, 2, 100, 90), 2000.0)
        self.assertEqual(calculate_position_size(10000, 0, 100, 90), 0.0)  # Edge case
        self.assertEqual(calculate_position_size(10000, 2, 100, 100), 0.0)  # Edge case

    def test_format_price(self):
        """Test price formatting"""
        self.assertEqual(format_price(100.5678), "100.57")
        self.assertEqual(format_price(100.5678, 3), "100.568")
        self.assertEqual(format_price(100), "100.00")

    def test_calculate_moving_average(self):
        """Test moving average calculation"""
        data = [1, 2, 3, 4, 5]
        self.assertEqual(calculate_moving_average(data, 3), 4.0)
        self.assertIsNone(calculate_moving_average(data, 6))  # Not enough data
        self.assertIsNone(calculate_moving_average([], 3))  # Empty data

    def test_calculate_volatility(self):
        """Test volatility calculation"""
        data = [100, 102, 98, 103, 97]
        vol = calculate_volatility(data)
        self.assertGreater(vol, 0)
        self.assertEqual(calculate_volatility([]), 0)  # Empty data

    def test_format_timestamp(self):
        """Test timestamp formatting"""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        self.assertEqual(
            format_timestamp(dt),
            "2023-01-01 12:00:00"
        )
        self.assertEqual(
            format_timestamp("2023-01-01T12:00:00Z"),
            "2023-01-01 12:00:00"
        )

    def test_calculate_win_rate(self):
        """Test win rate calculation"""
        trades = [
            {"profit": 100},
            {"profit": -50},
            {"profit": 75}
        ]
        self.assertAlmostEqual(calculate_win_rate(trades), 66.66666666666667, places=10)
        self.assertEqual(calculate_win_rate([]), 0)  # Empty trades

    def test_normalize_data(self):
        """Test data normalization"""
        data = [1, 2, 3, 4, 5]
        normalized = normalize_data(data)
        self.assertEqual(min(normalized), 0)
        self.assertEqual(max(normalized), 1)
        self.assertEqual(normalize_data([]), [])  # Empty data
        self.assertEqual(normalize_data([1, 1, 1]), [0.5, 0.5, 0.5])  # Same values

    def test_calculate_correlation(self):
        """Test correlation calculation"""
        data1 = [1, 2, 3, 4, 5]
        data2 = [2, 4, 6, 8, 10]
        self.assertAlmostEqual(calculate_correlation(data1, data2), 1.0, places=10)
        self.assertEqual(calculate_correlation([], []), 0)  # Empty data
        self.assertEqual(calculate_correlation([1], [1]), 0)  # Single value

    def test_format_percentage(self):
        """Test percentage formatting"""
        self.assertEqual(format_percentage(10.5678), "10.57%")
        self.assertEqual(format_percentage(10.5678, 3), "10.568%")
        self.assertEqual(format_percentage(0), "0.00%")

    def test_calculate_drawdown(self):
        """Test drawdown calculation"""
        data = [100, 95, 90, 95, 100, 85]
        result = calculate_drawdown(data)
        self.assertIn("max_drawdown", result)
        self.assertIn("current_drawdown", result)
        self.assertEqual(calculate_drawdown([]), {"max_drawdown": 0, "current_drawdown": 0})

class TestLogger(unittest.TestCase):
    def setUp(self):
        """Setup test environment"""
        # Clean up any existing logs
        cleanup_logs()
        
        # Create logs directory with absolute path
        self.log_dir = Path(os.getcwd()) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup test logger
        self.logger = setup_logger()

    def tearDown(self):
        """Cleanup test environment"""
        # Clean up logs
        cleanup_logs()

    def test_logger_setup(self):
        """Test logger setup"""
        logger = setup_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.INFO)
        self.assertTrue(any(isinstance(h, logging.FileHandler) for h in logger.handlers))
        self.assertTrue(any(isinstance(h, logging.StreamHandler) for h in logger.handlers))

    def test_get_logger(self):
        """Test getting logger instance"""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        self.assertEqual(logger1, logger2)  # Same module should get same logger
        self.assertEqual(logger1.name, "trade_analyzer.test_module")

    def test_logger_mixin(self):
        """Test logger mixin"""
        class TestClass(LoggerMixin):
            def __init__(self):
                pass

        test_obj = TestClass()
        self.assertIsInstance(test_obj.logger, logging.Logger)
        self.assertEqual(test_obj.logger.name, f"trade_analyzer.{TestClass.__name__}")

    def test_log_execution_time(self):
        """Test execution time logging decorator"""
        @log_execution_time
        def test_function():
            return "test"

        result = test_function()
        self.assertEqual(result, "test")

    def test_log_levels(self):
        """Test different log levels"""
        # Create a new logger for this test
        logger = get_logger("test_levels")
        
        # Create a specific log file for this test
        log_file = self.log_dir / "test_levels.log"
        handler = logging.FileHandler(str(log_file))
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(handler)
        
        # Test all log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Force logger to flush and close handlers
        for h in logger.handlers:
            h.flush()
            if isinstance(h, logging.FileHandler):
                h.close()
        
        # Give the file system a moment to complete writing
        time.sleep(0.1)
        
        # Verify log file exists
        self.assertTrue(log_file.exists(), "Log file was not created")
        
        # Read and verify log content
        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn("Info message", content)
            self.assertIn("Warning message", content)
            self.assertIn("Error message", content)
            self.assertIn("Critical message", content)

    def test_error_handling(self):
        """Test logger error handling"""
        logger = get_logger("test_errors")
        
        # Test logging with invalid parameters
        logger.info(None)  # Should handle None message
        logger.error(Exception("Test error"))  # Should handle exception objects

if __name__ == '__main__':
    unittest.main()
