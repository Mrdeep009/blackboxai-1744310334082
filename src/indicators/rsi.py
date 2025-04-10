import numpy as np
from typing import List, Optional
from ..utils.logger import get_logger

class RSIIndicator:
    def __init__(self, period: int = 14):
        """
        Initialize RSI indicator
        
        Args:
            period (int): RSI calculation period (default: 14)
        """
        self.period = period
        self.logger = get_logger(__name__)

    def calculate(self, prices: Optional[List[float]]) -> Optional[float]:
        """
        Calculate RSI value
        
        Args:
            prices (List[float]): List of closing prices
            
        Returns:
            Optional[float]: RSI value or None if calculation fails
        """
        try:
            if not isinstance(prices, (list, np.ndarray)) or not prices:
                return None
                
            if len(prices) < self.period:
                return None
                
            # Convert to numpy array
            price_array = np.array(prices)
            
            # Calculate price changes
            changes = np.diff(price_array)
            
            if len(changes) < self.period:
                return None
                
            # Separate gains and losses
            gains = np.where(changes > 0, changes, 0)
            losses = np.where(changes < 0, -changes, 0)
            
            # Calculate average gains and losses
            avg_gain = self._calculate_average(gains)
            avg_loss = self._calculate_average(losses)
            
            if avg_loss == 0:
                return 100.0
                
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi)
            
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            return None

    def _calculate_average(self, values: np.ndarray) -> float:
        """
        Calculate average for RSI
        
        Args:
            values (np.ndarray): Array of values
            
        Returns:
            float: Calculated average
        """
        try:
            if len(values) < self.period:
                return 0
                
            # Calculate initial average
            avg = np.mean(values[:self.period])
            
            # Calculate subsequent averages
            for value in values[self.period:]:
                avg = ((avg * (self.period - 1)) + value) / self.period
                
            return float(avg)
            
        except Exception as e:
            self.logger.error(f"Error calculating average: {str(e)}")
            return 0

    def get_signal(self, rsi: float) -> str:
        """
        Get trading signal based on RSI value
        
        Args:
            rsi (float): RSI value
            
        Returns:
            str: Trading signal
        """
        try:
            if rsi is None:
                return "neutral"
                
            if rsi > 70:
                return "overbought"
            elif rsi < 30:
                return "oversold"
            return "neutral"
            
        except Exception as e:
            self.logger.error(f"Error generating RSI signal: {str(e)}")
            return "neutral"

    def get_trend_strength(self, rsi: float) -> str:
        """
        Get trend strength based on RSI value
        
        Args:
            rsi (float): RSI value
            
        Returns:
            str: Trend strength
        """
        try:
            if rsi is None:
                return "weak"
                
            if rsi > 80 or rsi < 20:
                return "strong"
            elif rsi > 60 or rsi < 40:
                return "moderate"
            return "weak"
            
        except Exception as e:
            self.logger.error(f"Error calculating trend strength: {str(e)}")
            return "weak"

    def is_divergence(
        self,
        prices: List[float],
        rsi_values: List[float]
    ) -> bool:
        """
        Check for RSI divergence
        
        Args:
            prices (List[float]): List of prices
            rsi_values (List[float]): List of RSI values
            
        Returns:
            bool: True if divergence is detected
        """
        try:
            if not prices or not rsi_values or len(prices) != len(rsi_values):
                return False
                
            # Check for bullish divergence
            if prices[-1] < prices[-2] and rsi_values[-1] > rsi_values[-2]:
                return True
                
            # Check for bearish divergence
            if prices[-1] > prices[-2] and rsi_values[-1] < rsi_values[-2]:
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking RSI divergence: {str(e)}")
            return False
