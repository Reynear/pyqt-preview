"""
Tests for PyQt Preview configuration module.
"""

import tempfile
from pathlib import Path

from pyqt_preview.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.framework == "auto"
        assert config.ui_compiler == "auto"
        assert config.watch_patterns == ["*.py", "*.ui"]
        assert "__pycache__" in config.ignore_patterns
        assert config.reload_delay == 0.5
        assert config.preserve_window_state is True
        assert config.watch_dir == "."
        assert config.ui_dir is None
        assert config.verbose is False

    def test_config_from_args(self):
        """Test creating config from arguments."""
        config = Config.from_args(framework="pyqt6", reload_delay=1.0, verbose=True)

        assert config.framework == "pyqt6"
        assert config.reload_delay == 1.0
        assert config.verbose is True
        # Other values should be defaults
        assert config.ui_compiler == "auto"

    def test_config_merge(self):
        """Test merging configurations."""
        base_config = Config(framework="pyqt5", reload_delay=0.5)
        override_config = Config(framework="pyqt6", verbose=True)

        merged = base_config.merge(override_config)

        assert merged.framework == "pyqt6"  # From override
        assert merged.verbose is True  # From override
        assert merged.reload_delay == 0.5  # From base (override has default)

    def test_detect_framework_fallback(self):
        """Test framework detection fallback."""
        config = Config(framework="auto")
        detected = config.detect_framework()

        # Should return a valid framework (fallback to pyqt6)
        assert detected in ["pyqt5", "pyqt6", "pyside2", "pyside6"]

    def test_get_ui_compiler_command(self):
        """Test UI compiler command mapping."""
        test_cases = [
            ("pyqt5", "pyuic5"),
            ("pyqt6", "pyuic6"),
            ("pyside2", "pyside2-uic"),
            ("pyside6", "pyside6-uic"),
        ]

        for framework, expected_compiler in test_cases:
            config = Config(framework=framework)
            assert config.get_ui_compiler_command() == expected_compiler

    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = Config()
        errors = config.validate()

        # Should have no errors (current directory exists)
        assert len(errors) == 0

    def test_validate_invalid_framework(self):
        """Test validation with invalid framework."""
        config = Config(framework="invalid")
        errors = config.validate()

        assert len(errors) > 0
        assert any("Invalid framework" in error for error in errors)

    def test_validate_negative_delay(self):
        """Test validation with negative reload delay."""
        config = Config(reload_delay=-1.0)
        errors = config.validate()

        assert len(errors) > 0
        assert any("reload_delay must be non-negative" in error for error in errors)

    def test_validate_nonexistent_directory(self):
        """Test validation with nonexistent watch directory."""
        config = Config(watch_dir="/nonexistent/directory")
        errors = config.validate()

        assert len(errors) > 0
        assert any("does not exist" in error for error in errors)

    def test_config_from_toml_file(self):
        """Test loading configuration from TOML file."""
        toml_content = """
[tool.pyqt-preview]
framework = "pyqt5"
reload_delay = 1.5
verbose = true
watch_patterns = ["*.py"]
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            config_path = Path(f.name)

        try:
            config = Config.from_file(config_path)

            assert config.framework == "pyqt5"
            assert config.reload_delay == 1.5
            assert config.verbose is True
            assert config.watch_patterns == ["*.py"]

        finally:
            config_path.unlink()

    def test_config_from_missing_file(self):
        """Test loading configuration from missing file."""
        config = Config.from_file(Path("/nonexistent/file.toml"))

        # Should return default config without errors
        assert config.framework == "auto"
        assert config.reload_delay == 0.5

    def test_config_with_custom_patterns(self):
        """Test configuration with custom watch and ignore patterns."""
        config = Config(
            watch_patterns=["*.py", "*.qml"],
            ignore_patterns=["*.pyc", "venv/", ".git/"],
        )

        assert "*.qml" in config.watch_patterns
        assert "venv/" in config.ignore_patterns

    def test_config_output_dir_property(self):
        """Test config output_dir property when not defined."""
        config = Config()
        # Should have output_dir property that defaults to None
        assert hasattr(config, "output_dir")

    def test_config_framework_detection_hierarchy(self):
        """Test framework detection tries multiple options."""
        config = Config(framework="auto")

        # This should not crash and return a valid framework
        detected = config.detect_framework()
        assert detected in ["pyqt5", "pyqt6", "pyside2", "pyside6"]

    def test_config_validation_edge_cases(self):
        """Test config validation with edge cases."""
        # Very small but valid delay
        config = Config(reload_delay=0.01)
        errors = config.validate()
        assert len(errors) == 0

        # Zero delay should be valid
        config = Config(reload_delay=0.0)
        errors = config.validate()
        assert len(errors) == 0

    def test_config_merge_preserves_defaults(self):
        """Test that merge preserves default values correctly."""
        base = Config()
        override = Config(framework="pyqt5")  # Only change framework

        merged = base.merge(override)

        # Should have the override value
        assert merged.framework == "pyqt5"
        # Should preserve other defaults
        assert merged.reload_delay == 0.5
        assert merged.preserve_window_state is True
        assert merged.watch_patterns == ["*.py", "*.ui"]

    def test_config_string_representation(self):
        """Test config string representation if implemented."""
        config = Config(framework="pyqt6", verbose=True)

        # Should be able to convert to string without error
        str_repr = str(config)
        assert isinstance(str_repr, str)

    def test_config_equality_if_implemented(self):
        """Test config equality comparison if implemented."""
        config1 = Config(framework="pyqt6", reload_delay=1.0)
        config2 = Config(framework="pyqt6", reload_delay=1.0)
        config3 = Config(framework="pyqt5", reload_delay=1.0)

        # Test that configs with same values are treated consistently
        assert (config1 == config2) == (config1.__dict__ == config2.__dict__)
        assert (config1 == config3) == (config1.__dict__ == config3.__dict__)
