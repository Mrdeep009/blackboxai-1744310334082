import logging
import sys
import os
import time
from datetime import datetime
from typing import Optional
from pathlib import Path
from functools import wraps

# Global logger instance
_logger: Optional[logging.Logger] = None

def setup_logger() -> logging.Logger:
    """
    Setup and configure the application logger
    
    Returns:
        logging.Logger: Configured logger instance
    """
    global _logger
    
    if _logger is not None:
        return _logger
        
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True, mode=0o777)
        
        # Create logger
        logger = logging.getLogger("trade_analyzer")
        logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Setup file handler
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"trade_analyzer_{current_time}.log"
        
        # Create the log file
        log_file.touch(mode=0o666)
        
        file_handler = logging.FileHandler(str(log_file), mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Write initial log entry
        logger.info("Logger initialized")
        
        # Force flush handlers
        for handler in logger.handlers:
            handler.flush()
        
        _logger = logger
        return logger
        
    except Exception as e:
        # Fallback to basic console logging if file logging fails
        logger = logging.getLogger("trade_analyzer")
        logger.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
        
        logger.error(f"Failed to setup file logging: {str(e)}")
        return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name (str): Name of the module requesting the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logger()
    
    module_logger = logging.getLogger(f"trade_analyzer.{name}")
    module_logger.setLevel(_logger.level)
    
    # Ensure the module logger has the same handlers as the root logger
    if not module_logger.handlers:
        for handler in _logger.handlers:
            module_logger.addHandler(handler)
    
    return module_logger

class LoggerMixin:
    """
    Mixin class to add logging capability to any class
    """
    
    @property
    def logger(self) -> logging.Logger:
        """
        Get logger instance for the class
        
        Returns:
            logging.Logger: Logger instance
        """
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger

def log_execution_time(func):
    """
    Decorator to log function execution time
    
    Args:
        func: Function to be decorated
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(
                f"Function '{func.__name__}' executed in {execution_time:.2f} seconds"
            )
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function '{func.__name__}' failed after {execution_time:.2f} "
                f"seconds with error: {str(e)}"
            )
            raise
            
    return wrapper

def log_api_call(func):
    """
    Decorator to log API calls
    
    Args:
        func: Function to be decorated
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(f"API call: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"API call successful: {func.__name__}")
            return result
            
        except Exception as e:
            logger.error(f"API call failed: {func.__name__} - {str(e)}")
            raise
            
    return wrapper

def cleanup_logs():
    """
    Clean up old log files
    """
    try:
        log_dir = Path("logs")
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                try:
                    log_file.unlink()
                except Exception:
                    pass
            try:
                if not any(log_dir.iterdir()):
                    log_dir.rmdir()
            except Exception:
                pass
    except Exception:
        pass
