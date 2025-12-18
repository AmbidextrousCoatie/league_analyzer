# Logging Strategy

## Overview

The application uses Python's standard `logging` module with a simple wrapper service. This provides:
- **Zero dependencies** (uses standard library)
- **Multiple log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Multiple channels** (console, file)
- **Simple, clean API**
- **Centralized configuration**

## Core Principle

**NO `print()` statements anywhere in the codebase.** All output must go through the logging system.

## Quick Start

### Basic Usage

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debugging information")
logger.info("General informational message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
logger.exception("Exception occurred", exc_info=True)
```

### Setup (Application Startup)

```python
from pathlib import Path
from infrastructure.logging import setup_logging

# Setup logging once at application startup
setup_logging(
    level="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file=Path("logs/app.log"),  # Optional
    enable_file=True  # Enable file logging
)
```

## Log Levels

### DEBUG
- Detailed information for diagnosing problems
- Typically only enabled during development
- Example: "Processing player ID: 12345"

### INFO
- General informational messages about application flow
- Example: "Application started", "User logged in"

### WARNING
- Something unexpected happened, but application continues
- Example: "Configuration file not found, using defaults"

### ERROR
- Error occurred, but application can continue
- Example: "Failed to connect to database, retrying..."

### CRITICAL
- Serious error that may cause application to stop
- Example: "Database connection lost, cannot continue"

## Channels

### Console (stdout)
- Always enabled by default
- Useful for development and debugging
- Formatted output with timestamps

### File
- Optional, enabled via `enable_file=True`
- Useful for production logging
- Rotates automatically (via log rotation tools)

## Configuration

### Environment Variables

```bash
# Log level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log file path (optional)
LOG_FILE=logs/app.log

# Enable file logging
ENABLE_FILE_LOGGING=true
```

### Application Settings

Logging can be configured via `infrastructure.config.settings`:

```python
from infrastructure.config.settings import settings

setup_logging(
    level=settings.log_level,
    log_file=Path(settings.log_file) if settings.log_file else None,
    enable_file=bool(settings.log_file)
)
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ Good
logger.debug(f"Processing game {game_id}")
logger.info(f"Game {game_id} created successfully")
logger.warning(f"Handicap calculation returned None for player {player_id}")
logger.error(f"Failed to save game {game_id}: {error}")
logger.critical(f"Database connection lost: {error}")

# ❌ Bad
logger.info(f"Processing game {game_id}")  # Should be DEBUG
logger.error("Something happened")  # Too vague
```

### 2. Include Context

```python
# ✅ Good
logger.info(f"Creating league: {league_name} (season: {season})")
logger.error(f"Failed to calculate handicap for player {player_id}: {error}")

# ❌ Bad
logger.info("Creating league")
logger.error("Failed")
```

### 3. Use Exception Logging for Errors

```python
# ✅ Good
try:
    result = calculate_handicap(player)
except Exception as e:
    logger.exception(f"Error calculating handicap for player {player_id}")
    raise

# ❌ Bad
try:
    result = calculate_handicap(player)
except Exception as e:
    logger.error(f"Error: {e}")  # Missing traceback
```

### 4. Don't Log Sensitive Information

```python
# ✅ Good
logger.info(f"User {user_id} logged in")

# ❌ Bad
logger.info(f"User {user_id} logged in with password {password}")
```

### 5. Use Structured Logging

```python
# ✅ Good
logger.info(f"Game created: id={game_id}, league={league_id}, week={week}")

# ❌ Bad
logger.info(f"Game created: {game}")  # May include too much info
```

## Examples

### Domain Layer

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)

class HandicapCalculator:
    @staticmethod
    def calculate_handicap(game_results, settings):
        logger.debug(f"Calculating handicap for {len(game_results)} games")
        
        if not settings.enabled:
            logger.debug("Handicap disabled, returning None")
            return None
        
        try:
            handicap = _calculate(game_results, settings)
            logger.info(f"Handicap calculated: {handicap.value}")
            return handicap
        except Exception as e:
            logger.exception(f"Error calculating handicap: {e}")
            raise
```

### Application Layer

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)

class CreateGameHandler:
    def handle(self, command):
        logger.info(f"Creating game: league={command.league_id}, week={command.week}")
        
        try:
            game = self._game_repository.create(command)
            logger.info(f"Game created: id={game.id}")
            return game
        except Exception as e:
            logger.error(f"Failed to create game: {e}")
            raise
```

### Infrastructure Layer

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)

class DatabaseAdapter:
    def save(self, entity):
        logger.debug(f"Saving {entity.__class__.__name__}: id={entity.id}")
        
        try:
            self._connection.save(entity)
            logger.debug(f"Successfully saved {entity.__class__.__name__}: id={entity.id}")
        except Exception as e:
            logger.exception(f"Database error saving {entity.__class__.__name__}: {e}")
            raise
```

## Integration with FastAPI

```python
from fastapi import FastAPI
from infrastructure.logging import setup_logging, get_logger
from infrastructure.config.settings import settings

# Setup logging at application startup
setup_logging(
    level=settings.log_level,
    log_file=Path(settings.log_file) if settings.log_file else None,
    enable_file=bool(settings.log_file)
)

logger = get_logger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
```

## Migration from print()

### Before (❌ Bad)

```python
def calculate_handicap(player):
    print(f"Calculating handicap for {player.name}")
    result = _calculate(player)
    print(f"Result: {result}")
    return result
```

### After (✅ Good)

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)

def calculate_handicap(player):
    logger.debug(f"Calculating handicap for {player.name}")
    result = _calculate(player)
    logger.debug(f"Handicap calculated: {result.value}")
    return result
```

## Testing

Logging can be tested using Python's `logging` test utilities:

```python
import logging
from unittest.mock import patch
from infrastructure.logging import get_logger

def test_logging():
    logger = get_logger(__name__)
    
    with patch.object(logger._logger, 'info') as mock_info:
        logger.info("Test message")
        mock_info.assert_called_once_with("Test message")
```

## Summary

- ✅ Use `infrastructure.logging.get_logger(__name__)` to get a logger
- ✅ Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Include context in log messages
- ✅ Use `logger.exception()` for exceptions
- ✅ Setup logging once at application startup
- ❌ Never use `print()` statements
- ❌ Don't log sensitive information
- ❌ Don't use wrong log levels

