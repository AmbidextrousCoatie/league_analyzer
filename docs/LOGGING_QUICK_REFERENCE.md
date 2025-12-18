# Logging Quick Reference

## Import

```python
from infrastructure.logging import get_logger
```

## Get Logger

```python
logger = get_logger(__name__)
```

## Log Levels

```python
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
logger.exception("Exception with traceback")
```

## Setup (Application Startup)

```python
from infrastructure.logging import setup_logging
from pathlib import Path

setup_logging(
    level="INFO",
    log_file=Path("logs/app.log"),
    enable_file=True
)
```

## Common Patterns

### Domain Layer
```python
logger.debug(f"Calculating handicap for player {player_id}")
logger.info(f"Handicap calculated: {handicap.value}")
```

### Application Layer
```python
logger.info(f"Processing command: {command.__class__.__name__}")
logger.error(f"Command failed: {error}")
```

### Infrastructure Layer
```python
logger.debug(f"Saving entity: {entity.id}")
logger.exception(f"Database error: {error}")
```

## Rules

- ✅ Always use `get_logger(__name__)`
- ✅ Use appropriate log levels
- ✅ Include context in messages
- ✅ Use `logger.exception()` for exceptions
- ❌ Never use `print()`
- ❌ Don't log sensitive data

