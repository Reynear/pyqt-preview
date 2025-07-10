"""
Logging setup for PyQt Preview development tool.
"""

import logging
import sys
from typing import Optional


def setup_logging(verbose: bool = False) -> None:
    """
    Setup basic console logging for development.

    Args:
        verbose: Enable verbose output
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Simple console formatter
    formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Add console handler
    root_logger.addHandler(console_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to calling module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
