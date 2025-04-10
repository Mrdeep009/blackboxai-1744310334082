import random
import time
from typing import Optional, List
from datetime import datetime, timedelta
from ..utils.logger import get_logger

class APIKeyManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.keys = []
        self.key_usage = {}
        self.last_key_rotation = datetime.now()
        
        # Initialize with some pre-generated free API keys
        self._initialize_keys()

    def _initialize_keys(self):
        """Initialize the pool of API keys"""
        # These are example keys - you should replace with your own pre-generated keys
        initial_keys = [
            "DEMO_KEY1",
            "DEMO_KEY2",
            "DEMO_KEY3",
            "DEMO_KEY4",
            "DEMO_KEY5"
        ]
        
        for key in initial_keys:
            self.keys.append(key)
            self.key_usage[key] = {
                'count': 0,
                'last_used': None,
                'daily_limit': 25,
                'minute_limit': 5
            }

    def get_api_key(self) -> str:
        """
        Get an available API key
        
        Returns:
            str: A valid API key
        """
        try:
            # Check if we need to reset daily counts
            self._check_daily_reset()
            
            # Get available keys
            available_keys = self._get_available_keys()
            
            if not available_keys:
                # If no keys available, wait for rate limit reset
                self.logger.warning("No API keys available. Waiting for rate limit reset...")
                time.sleep(60)  # Wait for a minute
                return self.get_api_key()
            
            # Get least used key
            selected_key = self._get_least_used_key(available_keys)
            
            # Update usage
            self._update_key_usage(selected_key)
            
            return selected_key
            
        except Exception as e:
            self.logger.error(f"Error getting API key: {str(e)}")
            return self.keys[0]  # Return first key as fallback

    def _check_daily_reset(self):
        """Check and reset daily usage counts if needed"""
        now = datetime.now()
        if now - self.last_key_rotation >= timedelta(days=1):
            self.logger.info("Resetting daily API key usage counts")
            for key in self.keys:
                self.key_usage[key]['count'] = 0
            self.last_key_rotation = now

    def _get_available_keys(self) -> List[str]:
        """
        Get list of available API keys
        
        Returns:
            List[str]: List of available keys
        """
        available = []
        now = datetime.now()
        
        for key in self.keys:
            usage = self.key_usage[key]
            
            # Check daily limit
            if usage['count'] >= usage['daily_limit']:
                continue
            
            # Check minute limit
            if usage['last_used']:
                time_diff = now - usage['last_used']
                if time_diff < timedelta(minutes=1) and usage.get('minute_count', 0) >= usage['minute_limit']:
                    continue
            
            available.append(key)
        
        return available

    def _get_least_used_key(self, available_keys: List[str]) -> str:
        """
        Get the least used key from available keys
        
        Args:
            available_keys (List[str]): List of available keys
            
        Returns:
            str: Least used key
        """
        return min(
            available_keys,
            key=lambda k: (
                self.key_usage[k]['count'],
                self.key_usage[k]['last_used'] or datetime.min
            )
        )

    def _update_key_usage(self, key: str):
        """
        Update usage statistics for a key
        
        Args:
            key (str): API key to update
        """
        now = datetime.now()
        usage = self.key_usage[key]
        
        # Update counts
        usage['count'] += 1
        if usage['last_used'] and now - usage['last_used'] < timedelta(minutes=1):
            usage['minute_count'] = usage.get('minute_count', 0) + 1
        else:
            usage['minute_count'] = 1
        
        usage['last_used'] = now

    def report_error(self, key: str, error_message: str):
        """
        Report an error with an API key
        
        Args:
            key (str): API key that had an error
            error_message (str): Error message
        """
        if "rate limit" in error_message.lower():
            usage = self.key_usage[key]
            usage['count'] = usage['daily_limit']  # Mark as exhausted
            self.logger.warning(f"API key {key} has reached its rate limit")
