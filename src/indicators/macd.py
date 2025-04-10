import numpy as np
from typing import List, Optional, Tuple
from ..utils.logger import get_logger

class MACDIndicator:
    def __init__(self, fast_period: int, slow_period: int, signal_period: int):
        """
        Initialize MACD with customizable periods
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.logger = get_logger(__name__)

    def calculate(self, prices: List[float]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate MACD line, signal line, and histogram
        """
        try:
            if not isinstance(prices, (list, np.ndarray)) or len(prices) < self.slow_period + self.signal_period:
                return None, None, None

            prices_array = np.array(prices, dtype=float)
            
            # Calculate EMAs
            fast_ema = self._calculate_ema_array(prices_array, self.fast_period)
            slow_ema = self._calculate_ema_array(prices_array, self.slow_period)
            
            if fast_ema is None or slow_ema is None:
                return None, None, None
            
            # Calculate MACD line
            macd_line = fast_ema - slow_ema
            
            # Calculate Signal line
            signal_line = self._calculate_ema_array(macd_line, self.signal_period)
            
            if signal_line is None:
                return None, None, None
            
            # Calculate Histogram
            histogram = macd_line[-1] - signal_line[-1]
            
            return float(macd_line[-1]), float(signal_line[-1]), float(histogram)
            
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}")
            return None, None, None

    def _calculate_ema_array(self, data: np.ndarray, period: int) -> Optional[np.ndarray]:
        """
        Calculate EMA for the entire array
        """
        try:
            if len(data) < period:
                return None
            
            # Calculate multiplier
            multiplier = 2 / (period + 1)
            
            # Initialize EMA array
            ema = np.zeros_like(data)
            
            # Set first value as SMA
            ema[:period] = np.mean(data[:period])
            
            # Calculate EMA for remaining values
            for i in range(period, len(data)):
                ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
            
            return ema
            
        except Exception as e:
            self.logger.error(f"Error calculating EMA array: {str(e)}")
            return None

    def get_signal(self, macd: float, signal: float, hist: float) -> str:
        """
        Get trading signal based on MACD values
        """
        try:
            if macd is None or signal is None or hist is None:
                return 'neutral'
            
            # Strong buy signals
            if macd > signal and hist > 0 and macd > 0:
                return 'strong_buy'
            
            # Strong sell signals
            if macd < signal and hist < 0 and macd < 0:
                return 'strong_sell'
            
            # Buy signals
            if macd > signal and hist > 0:
                return 'buy'
            
            # Sell signals
            if macd < signal and hist < 0:
                return 'sell'
            
            return 'neutral'
            
        except Exception as e:
            self.logger.error(f"Error generating MACD signal: {str(e)}")
            return 'neutral'

    def get_trend_strength(self, histogram: float) -> str:
        """
        Get trend strength based on histogram value
        """
        try:
            if histogram is None:
                return 'weak'
            
            abs_hist = abs(histogram)
            
            if abs_hist > 0.5:
                return 'strong'
            elif abs_hist > 0.2:
                return 'moderate'
            else:
                return 'weak'
                
        except Exception as e:
            self.logger.error(f"Error calculating trend strength: {str(e)}")
            return 'weak'

    def is_divergence(self, prices: List[float], macd_values: List[float]) -> bool:
        """
        Check for MACD divergence
        """
        try:
            if len(prices) < 2 or len(macd_values) < 2:
                return False
            
            # Check for bullish divergence
            if prices[-1] < prices[-2] and macd_values[-1] > macd_values[-2]:
                return True
            
            # Check for bearish divergence
            if prices[-1] > prices[-2] and macd_values[-1] < macd_values[-2]:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking MACD divergence: {str(e)}")
            return False
