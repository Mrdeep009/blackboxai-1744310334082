import numpy as np
from typing import Dict, List, Optional, Tuple
from ..utils.logger import get_logger

class VolumeAnalyzer:
    def __init__(self):
        self.logger = get_logger(__name__)

    def analyze_volume(
        self,
        prices: List[float],
        volumes: List[float]
    ) -> Dict[str, any]:
        """
        Analyze volume patterns and indicators
        """
        try:
            if not isinstance(prices, (list, np.ndarray)) or not isinstance(volumes, (list, np.ndarray)) or len(prices) != len(volumes):
                return self._get_empty_result()

            if len(prices) < 2:
                return self._get_empty_result()

            volume_sma = self._calculate_volume_sma(volumes)
            price_volume_correlation = self._calculate_price_volume_correlation(
                prices, volumes
            )
            volume_trend = self._analyze_volume_trend(volumes)
            unusual_volume = self._detect_unusual_volume(volumes)
            
            return {
                "average_volume": 0 if volume_sma is None else float(volume_sma),
                "volume_trend": volume_trend,
                "price_volume_correlation": price_volume_correlation,
                "unusual_volume": unusual_volume,
                "volume_signal": self._generate_volume_signal(
                    volumes[-1] if volumes else 0,
                    volume_sma if volume_sma is not None else 0,
                    volume_trend,
                    unusual_volume
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error in volume analysis: {str(e)}")
            return self._get_empty_result()

    def _calculate_volume_sma(
        self,
        volumes: List[float],
        period: int = 20
    ) -> Optional[float]:
        """
        Calculate Simple Moving Average of volume
        """
        try:
            if len(volumes) < period:
                return 0
            return float(np.mean(volumes[-period:]))
        except Exception as e:
            self.logger.error(f"Error calculating volume SMA: {str(e)}")
            return 0

    def _calculate_price_volume_correlation(
        self,
        prices: List[float],
        volumes: List[float],
        period: int = 20
    ) -> float:
        """
        Calculate correlation between price and volume
        """
        try:
            if len(prices) < period or len(volumes) < period:
                return 0
                
            price_changes = np.diff(prices[-period:])
            volume_changes = np.diff(volumes[-period:])
            
            if len(price_changes) != len(volume_changes):
                return 0
                
            correlation = float(np.corrcoef(price_changes, volume_changes)[0, 1])
            return 0 if np.isnan(correlation) else correlation
            
        except Exception as e:
            self.logger.error(
                f"Error calculating price-volume correlation: {str(e)}"
            )
            return 0

    def _analyze_volume_trend(
        self,
        volumes: List[float],
        period: int = 10
    ) -> str:
        """
        Analyze volume trend
        """
        try:
            if len(volumes) < period:
                return "neutral"
                
            recent_volumes = volumes[-period:]
            volume_trend = np.polyfit(range(len(recent_volumes)), recent_volumes, 1)[0]
            
            if volume_trend > 0:
                return "increasing"
            elif volume_trend < 0:
                return "decreasing"
            return "neutral"
            
        except Exception as e:
            self.logger.error(f"Error analyzing volume trend: {str(e)}")
            return "neutral"

    def _detect_unusual_volume(
        self,
        volumes: List[float],
        period: int = 20,
        threshold: float = 2.0
    ) -> bool:
        """
        Detect unusual volume activity
        """
        try:
            if len(volumes) < period:
                return False
                
            recent_volumes = volumes[-period:]
            mean_volume = np.mean(recent_volumes)
            std_volume = np.std(recent_volumes)
            
            if std_volume == 0:
                return False
                
            current_volume = volumes[-1]
            z_score = (current_volume - mean_volume) / std_volume
            
            return abs(z_score) > threshold
            
        except Exception as e:
            self.logger.error(f"Error detecting unusual volume: {str(e)}")
            return False

    def _generate_volume_signal(
        self,
        current_volume: float,
        avg_volume: float,
        volume_trend: str,
        unusual_volume: bool
    ) -> str:
        """
        Generate trading signal based on volume analysis
        """
        try:
            # Strong volume signals
            if current_volume > (avg_volume * 2) and volume_trend == "increasing":
                return "strong_volume"
                
            # Weak volume signals
            if current_volume < (avg_volume * 0.5) and volume_trend == "decreasing":
                return "weak_volume"
                
            # Unusual volume signals
            if unusual_volume:
                return "unusual_volume"
                
            return "normal_volume"
            
        except Exception as e:
            self.logger.error(f"Error generating volume signal: {str(e)}")
            return "normal_volume"

    def _get_empty_result(self) -> Dict[str, any]:
        """
        Get empty result dictionary
        """
        return {
            "average_volume": 0,
            "volume_trend": "neutral",
            "price_volume_correlation": 0,
            "unusual_volume": False,
            "volume_signal": "normal_volume"
        }

    def get_volume_strength(self, volume_data: Dict[str, any]) -> str:
        """
        Get volume strength indication
        """
        try:
            if volume_data["volume_signal"] == "strong_volume":
                return "strong"
            elif volume_data["volume_signal"] == "weak_volume":
                return "weak"
            elif volume_data["unusual_volume"]:
                return "unusual"
            return "normal"
            
        except Exception as e:
            self.logger.error(f"Error getting volume strength: {str(e)}")
            return "normal"

    def is_volume_confirming_trend(
        self,
        price_trend: str,
        volume_data: Dict[str, any]
    ) -> bool:
        """
        Check if volume confirms price trend
        """
        try:
            if price_trend == "uptrend" and volume_data["volume_trend"] == "increasing":
                return True
            if price_trend == "downtrend" and volume_data["volume_trend"] == "decreasing":
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking volume confirmation: {str(e)}")
            return False
