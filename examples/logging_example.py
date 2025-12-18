"""
Example: Using the Logging System

This demonstrates how to use the logging infrastructure across different layers.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.logging import setup_logging, get_logger

# Setup logging once at application startup
setup_logging(
    level="DEBUG",  # Set to DEBUG to see all messages
    log_file=Path("logs/example.log"),
    enable_file=True
)

# Get logger for this module
logger = get_logger(__name__)

def example_domain_layer():
    """Example: Domain layer logging"""
    logger.debug("Domain layer: Starting handicap calculation")
    logger.info("Domain layer: Handicap calculated successfully")
    logger.warning("Domain layer: Handicap exceeds maximum, capping at 50")

def example_application_layer():
    """Example: Application layer logging"""
    logger.info("Application layer: Processing CreateGame command")
    logger.debug("Application layer: Command validated, creating game")
    logger.error("Application layer: Failed to create game - validation error")

def example_infrastructure_layer():
    """Example: Infrastructure layer logging"""
    logger.debug("Infrastructure layer: Connecting to database")
    logger.info("Infrastructure layer: Database connection established")
    logger.warning("Infrastructure layer: Database query took longer than expected")

def example_exception_logging():
    """Example: Exception logging"""
    try:
        result = 1 / 0
    except Exception as e:
        logger.exception("Exception occurred during calculation")
        # This will log the full traceback

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Logging Example Started")
    logger.info("=" * 50)
    
    example_domain_layer()
    example_application_layer()
    example_infrastructure_layer()
    example_exception_logging()
    
    logger.info("=" * 50)
    logger.info("Logging Example Completed")
    logger.info("=" * 50)

