"""
Basic path validation for PyQt Preview development tool.
"""

import os
from pathlib import Path
from typing import Union


class SecurityError(Exception):
    """Raised when a basic validation fails."""


def validate_python_file(file_path: Union[str, Path]) -> Path:
    """
    Basic validation for Python script files.

    Args:
        file_path: Path to the Python script

    Returns:
        Validated Path object

    Raises:
        SecurityError: If the file is invalid
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Must be a Python file
    if file_path.suffix.lower() != ".py":
        raise SecurityError(f"Script must be a Python file: {file_path}")

    # Must exist and be a file
    if not file_path.exists():
        raise SecurityError(f"Script file does not exist: {file_path}")

    if not file_path.is_file():
        raise SecurityError(f"Script path is not a file: {file_path}")

    # Check if readable
    if not os.access(file_path, os.R_OK):
        raise SecurityError(f"Script file is not readable: {file_path}")

    return file_path.resolve()


def validate_ui_file(file_path: Union[str, Path]) -> Path:
    """
    Basic validation for UI files.

    Args:
        file_path: Path to the UI file

    Returns:
        Validated Path object

    Raises:
        SecurityError: If the file is invalid
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Must be a UI file
    if file_path.suffix.lower() != ".ui":
        raise SecurityError(f"File must be a UI file: {file_path}")

    # Must exist and be a file
    if not file_path.exists():
        raise SecurityError(f"UI file does not exist: {file_path}")

    if not file_path.is_file():
        raise SecurityError(f"UI path is not a file: {file_path}")

    return file_path.resolve()
