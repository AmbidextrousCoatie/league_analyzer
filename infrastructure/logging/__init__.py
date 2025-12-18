"""
Logging infrastructure.

Provides a simple, centralized logging service for the application.
"""

from infrastructure.logging.logger import get_logger, Logger, setup_logging

__all__ = ["get_logger", "Logger", "setup_logging"]

