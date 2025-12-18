"""
Logger Service

Simple, centralized logging service using Python's standard logging module.
Provides a clean interface for logging across the application.

Usage:
    from infrastructure.logging import get_logger
    
    logger = get_logger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """
    Simple logger wrapper around Python's standard logging.Logger.
    
    Provides a clean interface for logging with multiple levels and channels.
    """
    
    def __init__(self, name: str):
        """
        Initialize logger.
        
        Args:
            name: Logger name (typically __name__)
        """
        self._logger = logging.getLogger(name)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, exc_info=True, **kwargs) -> None:
        """Log exception with traceback."""
        self._logger.exception(message, *args, exc_info=exc_info, **kwargs)


def get_logger(name: str) -> Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("Application started")
    """
    return Logger(name)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = False
) -> None:
    """
    Configure application-wide logging.
    
    This should be called once at application startup.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        format_string: Optional custom format string
        enable_console: Enable console output (default: True)
        enable_file: Enable file output (default: False, requires log_file)
    
    Example:
        setup_logging(
            level="DEBUG",
            log_file=Path("logs/app.log"),
            enable_file=True
        )
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Default format: timestamp - logger name - level - file:line - message
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    formatter = logging.Formatter(
        format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handlers = []
    
    # Console handler (stdout)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    # File handler
    if enable_file and log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set specific logger levels (reduce noise from third-party libraries)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

