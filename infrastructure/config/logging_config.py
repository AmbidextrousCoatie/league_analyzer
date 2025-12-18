"""
Logging configuration (deprecated).

This module is deprecated. Use infrastructure.logging instead.

For new code, use:
    from infrastructure.logging import get_logger, setup_logging
"""

import warnings
from pathlib import Path
from typing import Optional

# Import from new location
from infrastructure.logging.logger import (
    get_logger as _get_logger,
    setup_logging as _setup_logging,
    Logger
)

warnings.warn(
    "infrastructure.config.logging_config is deprecated. "
    "Use infrastructure.logging instead.",
    DeprecationWarning,
    stacklevel=2
)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Configure application logging (deprecated).
    
    Use infrastructure.logging.setup_logging instead.
    """
    enable_file = log_file is not None
    _setup_logging(
        level=level,
        log_file=log_file,
        format_string=format_string,
        enable_console=True,
        enable_file=enable_file
    )


def get_logger(name: str) -> Logger:
    """
    Get a logger instance (deprecated).
    
    Use infrastructure.logging.get_logger instead.
    """
    return _get_logger(name)

