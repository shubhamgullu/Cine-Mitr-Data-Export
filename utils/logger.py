"""
Logging configuration for CineMitr Dashboard
Provides centralized logging with multiple handlers and formatters
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

class DashboardLogger:
    """Centralized logging configuration for the dashboard application"""
    
    def __init__(self, name: str = "cinemitr_dashboard"):
        self.name = name
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup logger with file and console handlers"""
        self.logger = logging.getLogger(self.name)
        
        # Avoid duplicate handlers if logger already configured
        if self.logger.handlers:
            return
            
        # Set log level from environment or default to INFO
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_dir / f"{self.name}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Error file handler
        error_handler = RotatingFileHandler(
            log_dir / f"{self.name}_errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        
        # Log initialization
        self.logger.info(f"Logger initialized for {self.name}")
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger
    
    def log_api_call(self, method: str, url: str, status_code: Optional[int] = None, 
                     duration: Optional[float] = None) -> None:
        """Log API call details"""
        message = f"API {method} {url}"
        if status_code:
            message += f" - Status: {status_code}"
        if duration:
            message += f" - Duration: {duration:.2f}s"
        
        if status_code and status_code >= 400:
            self.logger.error(message)
        else:
            self.logger.info(message)
    
    def log_user_action(self, action: str, user_id: Optional[str] = None, 
                        details: Optional[dict] = None) -> None:
        """Log user actions for audit trail"""
        message = f"User Action: {action}"
        if user_id:
            message += f" - User: {user_id}"
        if details:
            message += f" - Details: {details}"
        
        self.logger.info(message)
    
    def log_performance(self, operation: str, duration: float, 
                       threshold: float = 1.0) -> None:
        """Log performance metrics"""
        message = f"Performance: {operation} took {duration:.2f}s"
        
        if duration > threshold:
            self.logger.warning(f"{message} (exceeds threshold of {threshold}s)")
        else:
            self.logger.debug(message)
    
    def log_error_with_context(self, error: Exception, context: dict) -> None:
        """Log errors with additional context"""
        self.logger.error(
            f"Error: {str(error)} | Context: {context}",
            exc_info=True
        )

# Global logger instance
dashboard_logger = DashboardLogger()
logger = dashboard_logger.get_logger()

def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance for a specific component"""
    if name:
        return DashboardLogger(name).get_logger()
    return logger

def setup_logger(name: str) -> logging.Logger:
    """Setup logger for a specific component (alias for get_logger)"""
    return get_logger(name)