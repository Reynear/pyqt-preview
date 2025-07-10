"""
PyQt Preview - Live preview tool for PyQt GUI development.

Provides real-time feedback when editing .py or .ui files for faster development.
"""

__version__ = "0.2.0"
__author__ = "Reynear Douglas"
__email__ = "douglasreynear@gmail.com"
__license__ = "MIT"
__description__ = "Live preview tool for PyQt GUI development"

from .compiler import UICompiler
from .config import Config, ConfigError
from .core import PreviewEngine
from .logging_config import get_logger, setup_logging
from .security import SecurityError, validate_python_file, validate_ui_file
from .watcher import FileWatcher

__all__ = [
    "Config",
    "ConfigError",
    "FileWatcher",
    "PreviewEngine",
    "SecurityError",
    "UICompiler",
    "get_logger",
    "setup_logging",
    "validate_python_file",
    "validate_ui_file",
]
