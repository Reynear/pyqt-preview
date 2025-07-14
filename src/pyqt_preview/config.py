"""
Configuration management for PyQt Preview development tool.
"""

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[import] # For Python <3.11, make sure tomli is installed


class ConfigError(Exception):
    """Raised when configuration validation fails."""


@dataclass
class Config:
    """Simple configuration for PyQt Preview development tool."""

    # Framework settings
    framework: str = "auto"  # auto, pyqt5, pyqt6, pyside2, pyside6
    ui_compiler: str = "auto"  # auto, pyuic5, pyuic6, pyside2-uic, pyside6-uic

    # File watching settings
    watch_patterns: list[str] = field(default_factory=lambda: ["*.py", "*.ui"])
    ignore_patterns: list[str] = field(
        default_factory=lambda: [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".git",
            ".venv",
            "venv",
            ".pytest_cache",
            "*.egg-info",
        ]
    )

    # Reload behavior
    reload_delay: float = 0.5
    preserve_window_state: bool = True

    # Directories
    watch_dir: str = "."
    ui_dir: Optional[str] = None
    output_dir: Optional[str] = None

    # Logging
    verbose: bool = False

    # Prevent PyQt window from stealing focus on macOS
    keep_window_focus: bool = False

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from a TOML file."""
        if config_path is None:
            # Look for config file in current directory
            config_path = Path(".pyqt-preview.toml")
            if not config_path.exists():
                config_path = Path("pyproject.toml")

        config_data: dict[str, Any] = {}
        if config_path.exists():
            if tomllib is None:
                print("Warning: tomllib not available. Please install tomli for Python < 3.11")
                return cls(**config_data)

            try:
                with config_path.open("rb") as f:
                    data = tomllib.load(f)

                # Extract pyqt-preview specific config
                if "tool" in data and "pyqt-preview" in data["tool"]:
                    config_data = data["tool"]["pyqt-preview"]
                elif "pyqt-preview" in data:
                    config_data = data["pyqt-preview"]

            except (OSError, tomllib.TOMLDecodeError) as e:
                print(f"Warning: Could not load config file {config_path}: {e}")

        return cls(**config_data)

    @classmethod
    def from_args(cls, **kwargs: Any) -> "Config":
        """Create configuration from command line arguments."""
        # Filter out None values
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return cls(**filtered_kwargs)

    def merge(self, other: "Config") -> "Config":
        """Merge this config with another, giving preference to the other."""
        merged_data = {}

        for field_name in self.__dataclass_fields__:
            self_value = getattr(self, field_name)
            other_value = getattr(other, field_name)

            # Use other's value if it's not the default
            if other_value != self.__dataclass_fields__[field_name].default:
                merged_data[field_name] = other_value
            else:
                merged_data[field_name] = self_value

        return Config(**merged_data)

    def detect_framework(self) -> str:
        """Auto-detect the GUI framework to use."""
        if self.framework != "auto":
            return self.framework

        # Try to detect based on imports in Python files
        try:
            importlib.util.find_spec("PyQt6")
            return "pyqt6"
        except ImportError:
            pass

        try:
            importlib.util.find_spec("PyQt5")
            return "pyqt5"
        except ImportError:
            pass

        try:
            importlib.util.find_spec("PySide6")
            return "pyside6"
        except ImportError:
            pass

        try:
            importlib.util.find_spec("PySide2")
            return "pyside2"
        except ImportError:
            pass

        # Default fallback
        return "pyqt6"

    def get_ui_compiler_command(self) -> str:
        """Get the appropriate UI compiler command."""
        if self.ui_compiler != "auto":
            return self.ui_compiler

        framework = self.detect_framework()

        compiler_map = {
            "pyqt5": "pyuic5",
            "pyqt6": "pyuic6",
            "pyside2": "pyside2-uic",
            "pyside6": "pyside6-uic",
        }

        return compiler_map.get(framework, "pyuic6")

    def validate(self) -> list[str]:
        """Validate the configuration and return list of errors."""
        errors = []

        # Check framework
        valid_frameworks = ["auto", "pyqt5", "pyqt6", "pyside2", "pyside6"]
        if self.framework not in valid_frameworks:
            errors.append(f"Invalid framework '{self.framework}'. Must be one of: {valid_frameworks}")

        # Check reload delay
        if self.reload_delay < 0:
            errors.append("reload_delay must be non-negative")

        # Check directories exist
        if not Path(self.watch_dir).exists():
            errors.append(f"Watch directory '{self.watch_dir}' does not exist")

        if self.ui_dir and not Path(self.ui_dir).exists():
            errors.append(f"UI directory '{self.ui_dir}' does not exist")

        return errors
