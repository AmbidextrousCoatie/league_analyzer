"""
Encoding Configuration

Sets UTF-8 encoding as default for Python file operations and console output.
This prevents encoding issues with Unicode characters (emojis, special chars).

Usage:
    import scripts.encoding_config  # Import at start of script
    # Now file operations will default to UTF-8
"""

import sys
import io
import os
from pathlib import Path


def configure_utf8():
    """
    Configure UTF-8 encoding for Python.
    
    Sets:
    - sys.stdout/stderr to UTF-8
    - PYTHONIOENCODING environment variable
    - Default encoding for file operations (Python 3.7+)
    """
    # Set environment variable for Python I/O encoding
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    # Reconfigure stdout/stderr to use UTF-8
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    
    if sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    
    # Set default encoding for open() (Python 3.10+)
    if hasattr(sys, "setdefaultencoding"):
        sys.setdefaultencoding("utf-8")


# Auto-configure when imported
configure_utf8()

# Export constant for explicit encoding in file operations
UTF8 = "utf-8"

