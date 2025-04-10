import numpy as np
from datetime import datetime
from typing import List, Dict, Union, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values
    """
    try:
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    except Exception as e:
        logger.error(f"Error calculating percentage change: {str(e)}")
        return 0

def calculate_risk_reward_ratio(
    entry_price: float,
    stop_loss: float,
    take_profit: float
) -> float:
    """
    Calculate risk/reward ratio for a trade
    """
    try:
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return 0
            
        return reward / risk
    except Exception as e:
        logger.error(f"Error calculating risk/reward ratio: {str(e)}")
        return 0

def calculate_position_size(
    account_size: float,
    risk_percentage: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calculate position size based on risk parameters
    """
    try:
        if entry_price == stop_loss:
            return 0
            
        risk_amount = account_size * (risk_percentage / 100)
        price_risk = abs(entry_price - stop_loss)
        
        position_size = (risk_amount / price_risk) * 100
        return position_size
    except Exception as e:
        logger.error(f"Error calculating position size: {str(e)}")
        return 0

def format_price(price: float, decimals: int = 2) -> str:
    """
    Format price with specified decimal places
    """
    try:
        return f"{price:.{decimals}f}"
    except Exception as e:
        logger.error(f"Error formatting price: {str(e)}")
        return str(price)

def calculate_moving_average(
    data: List[float],
    period: int
) -> Optional[float]:
    """
    Calculate simple moving average
    """
    try:
        if len(data) < period:
            return None
        return float(np.mean(data[-period:]))
    except Exception as e:
        logger.error(f"Error calculating moving average: {str(e)}")
        return None

def calculate_volatility(data: List[float], period: int = 14) -> float:
    """
    Calculate price volatility (standard deviation)
    """
    try:
        if len(data) < 2:
            return 0
        return float(np.std(data[-period:]))
    except Exception as e:
        logger.error(f"Error calculating volatility: {str(e)}")
        return 0

def format_timestamp(timestamp: Union[str, datetime]) -> str:
    """
    Format timestamp to standard string format
    """
    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.error(f"Error formatting timestamp: {str(e)}")
        return str(timestamp)

def calculate_win_rate(trades: List[Dict]) -> float:
    """
    Calculate win rate from list of trades
    """
    try:
        if not trades:
            return 0
            
        winning_trades = sum(1 for trade in trades if trade.get('profit', 0) > 0)
        return (winning_trades / len(trades)) * 100
    except Exception as e:
        logger.error(f"Error calculating win rate: {str(e)}")
        return 0

def normalize_data(data: List[float]) -> List[float]:
    """
    Normalize data to range [0, 1]
    """
    try:
        if not data:
            return []
            
        min_val = min(data)
        max_val = max(data)
        
        if max_val == min_val:
            return [0.5] * len(data)
            
        return [(x - min_val) / (max_val - min_val) for x in data]
    except Exception as e:
        logger.error(f"Error normalizing data: {str(e)}")
        return data

def calculate_correlation(data1: List[float], data2: List[float]) -> float:
    """
    Calculate correlation coefficient between two datasets
    """
    try:
        if len(data1) != len(data2) or len(data1) < 2:
            return 0
            
        correlation = float(np.corrcoef(data1, data2)[0, 1])
        return correlation if not np.isnan(correlation) else 0
    except Exception as e:
        logger.error(f"Error calculating correlation: {str(e)}")
        return 0

def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage string
    """
    try:
        return f"{value:.{decimals}f}%"
    except Exception as e:
        logger.error(f"Error formatting percentage: {str(e)}")
        return f"{value}%"

def calculate_drawdown(data: List[float]) -> Dict[str, float]:
    """
    Calculate maximum drawdown and current drawdown
    """
    try:
        if not data:
            return {"max_drawdown": 0, "current_drawdown": 0}
            
        peak = data[0]
        max_drawdown = 0
        current_drawdown = 0
        
        for value in data:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
            current_drawdown = drawdown
            
        return {
            "max_drawdown": max_drawdown,
            "current_drawdown": current_drawdown
        }
    except Exception as e:
        logger.error(f"Error calculating drawdown: {str(e)}")
        return {"max_drawdown": 0, "current_drawdown": 0}
