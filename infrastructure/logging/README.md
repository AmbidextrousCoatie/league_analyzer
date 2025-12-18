# Logging Infrastructure

Simple, lightweight logging service using Python's standard `logging` module.

## Features

- ✅ Zero dependencies (standard library only)
- ✅ Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Multiple channels (console, file)
- ✅ Simple, clean API
- ✅ Centralized configuration

## Usage

```python
from infrastructure.logging import get_logger

logger = get_logger(__name__)
logger.info("Application started")
```

## Setup

```python
from infrastructure.logging import setup_logging
from pathlib import Path

setup_logging(
    level="INFO",
    log_file=Path("logs/app.log"),
    enable_file=True
)
```

See `docs/LOGGING_STRATEGY.md` for complete documentation.

