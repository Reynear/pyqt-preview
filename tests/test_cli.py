"""
Comprehensive tests for PyQt Preview CLI module.
"""

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from pyqt_preview import __version__
from pyqt_preview.cli import app, main, version_callback
from pyqt_preview.config import Config


class TestCLI:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_callback_displays_version(self):
        """Test version callback displays correct version."""
        with pytest.raises(typer.Exit):
            version_callback(True)

    def test_version_callback_no_action_when_false(self):
        """Test version callback does nothing when False."""
        # Should not raise SystemExit
        result = version_callback(False)
        assert result is None

    def test_version_option_short(self):
        """Test --version/-v option displays version."""
        result = self.runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        # Strip ANSI color codes for comparison
        clean_output = result.stdout.replace("\x1b[1;36m", "").replace("\x1b[0m", "")
        assert __version__ in clean_output

    def test_version_option_long(self):
        """Test --version option displays version."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        # Strip ANSI color codes for comparison
        clean_output = result.stdout.replace("\x1b[1;36m", "").replace("\x1b[0m", "")
        assert __version__ in clean_output

    def test_no_args_shows_help(self):
        """Test that running without arguments shows help."""
        result = self.runner.invoke(app, [])
        # Typer apps with no_args_is_help=True exit with code 2 when no args provided
        assert result.exit_code == 2
        assert "Usage:" in result.stdout

    @patch("pyqt_preview.cli.PreviewEngine")
    def test_run_command_basic(self, mock_engine_class):
        """Test basic run command functionality."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('Hello, World!')")
            script_path = f.name

        try:
            # Mock the engine
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine

            result = self.runner.invoke(app, ["run", script_path])

            # Should succeed
            assert result.exit_code == 0

            # Engine should be created and run
            mock_engine_class.assert_called_once()
            mock_engine.run.assert_called_once()

        finally:
            Path(script_path).unlink()

    def test_run_command_nonexistent_script(self):
        """Test run command with nonexistent script."""
        result = self.runner.invoke(app, ["run", "/nonexistent/script.py"])
        assert result.exit_code == 1
        assert "Script not found" in result.stdout

    def test_run_command_non_python_file(self):
        """Test run command with non-Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("not python")
            file_path = f.name

        try:
            result = self.runner.invoke(app, ["run", file_path])
            assert result.exit_code == 1
            assert "must be a Python file" in result.stdout
        finally:
            Path(file_path).unlink()

    @patch("pyqt_preview.cli.PreviewEngine")
    @patch("pyqt_preview.cli.Config.validate")
    def test_run_command_with_options(self, mock_validate, mock_engine_class):
        """Test run command with various options."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            mock_validate.return_value = []  # No validation errors
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine

            with tempfile.TemporaryDirectory() as temp_dir:
                ui_dir = Path(temp_dir) / "ui"
                ui_dir.mkdir()

                result = self.runner.invoke(
                    app,
                    [
                        "run",
                        script_path,
                        "--watch",
                        temp_dir,
                        "--ui-dir",
                        str(ui_dir),
                        "--framework",
                        "pyqt6",
                        "--reload-delay",
                        "1.5",
                        "--preserve-state",
                        "--verbose",
                    ],
                )

                assert result.exit_code == 0
                mock_engine_class.assert_called_once()

                # Check that config was passed with correct values
                args, kwargs = mock_engine_class.call_args
                config = args[1]  # Second argument is config
                assert config.framework == "pyqt6"
                assert config.reload_delay == 1.5
                assert config.preserve_window_state is True
                assert config.verbose is True

        finally:
            Path(script_path).unlink()

    @patch("pyqt_preview.cli.Config.from_file")
    def test_run_command_with_config_file(self, mock_from_file):
        """Test run command with config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            # Mock config loading
            mock_config = Config(framework="pyqt5")
            mock_from_file.return_value = mock_config

            with patch("pyqt_preview.cli.PreviewEngine") as mock_engine_class:
                mock_engine = Mock()
                mock_engine_class.return_value = mock_engine

                with tempfile.TemporaryDirectory() as temp_dir:
                    config_file = Path(temp_dir) / "config.toml"
                    config_file.write_text("test config")

                    result = self.runner.invoke(app, ["run", script_path, "--config", str(config_file)])

                    assert result.exit_code == 0
                    mock_from_file.assert_called_once()

        finally:
            Path(script_path).unlink()

    @patch("pyqt_preview.cli.Config.validate")
    def test_run_command_config_validation_error(self, mock_validate):
        """Test run command with config validation errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            # Mock validation to return errors
            mock_validate.return_value = ["Invalid framework", "Invalid delay"]

            result = self.runner.invoke(app, ["run", script_path])
            assert result.exit_code == 1
            assert "Configuration errors" in result.stdout

        finally:
            Path(script_path).unlink()

    @patch("pyqt_preview.cli.PreviewEngine")
    def test_run_command_engine_exception(self, mock_engine_class):
        """Test run command when engine raises exception."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            # Mock engine to raise exception
            mock_engine = Mock()
            mock_engine.run.side_effect = RuntimeError("Engine failed")
            mock_engine_class.return_value = mock_engine

            result = self.runner.invoke(app, ["run", script_path])
            assert result.exit_code == 1
            assert "Fatal error" in result.stdout

        finally:
            Path(script_path).unlink()

    @patch("pyqt_preview.cli.PreviewEngine")
    def test_run_command_keyboard_interrupt(self, mock_engine_class):
        """Test run command handles KeyboardInterrupt gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            # Mock engine to raise KeyboardInterrupt
            mock_engine = Mock()
            mock_engine.run.side_effect = KeyboardInterrupt()
            mock_engine_class.return_value = mock_engine

            result = self.runner.invoke(app, ["run", script_path])
            assert result.exit_code == 0
            assert "Goodbye!" in result.stdout

        finally:
            Path(script_path).unlink()

    def test_init_command_basic(self):
        """Test basic init command functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(app, ["init", "--dir", temp_dir])
            assert result.exit_code == 0

            # Check that config file was created
            config_file = Path(temp_dir) / ".pyqt-preview.toml"
            assert config_file.exists()

            # Check config content
            content = config_file.read_text()
            assert "pyqt-preview" in content
            assert "framework" in content

    def test_init_command_with_framework(self):
        """Test init command with specific framework."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(app, ["init", "--dir", temp_dir, "--framework", "pyqt5"])
            assert result.exit_code == 0

            config_file = Path(temp_dir) / ".pyqt-preview.toml"
            content = config_file.read_text()
            assert 'framework = "pyqt5"' in content

    def test_init_command_current_directory(self):
        """Test init command defaults to current directory behavior."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to the temp directory and run init without --dir
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                result = self.runner.invoke(app, ["init"])
                assert result.exit_code == 0

                config_file = Path(temp_dir) / ".pyqt-preview.toml"
                assert config_file.exists()
            finally:
                os.chdir(original_cwd)

    def test_init_command_existing_config_no_force(self):
        """Test init command with existing config without force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / ".pyqt-preview.toml"
            config_file.write_text("existing config")

            result = self.runner.invoke(app, ["init", "--dir", temp_dir])
            assert result.exit_code == 1
            assert "already exists" in result.stdout

    def test_init_command_existing_config_with_force(self):
        """Test init command with existing config using force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / ".pyqt-preview.toml"
            config_file.write_text("existing config")

            result = self.runner.invoke(app, ["init", "--dir", temp_dir, "--force"])
            assert result.exit_code == 0

            # Config should be overwritten
            content = config_file.read_text()
            assert "pyqt-preview" in content
            assert "existing config" not in content

    @patch("pyqt_preview.cli.Config.from_file")
    def test_check_command_valid_config(self, mock_from_file):
        """Test check command with valid configuration."""
        mock_config = Config()
        mock_config.validate = Mock(return_value=[])
        mock_from_file.return_value = mock_config

        with (
            patch("pyqt_preview.compiler.UICompiler") as mock_compiler_class,
            patch("importlib.util.find_spec") as mock_find_spec,
        ):
            mock_compiler = Mock()
            mock_compiler.check_compiler_available.return_value = True
            mock_compiler.get_compiler_version.return_value = "6.4.0"
            mock_compiler_class.return_value = mock_compiler
            mock_find_spec.return_value = True  # Mock successful import

            result = self.runner.invoke(app, ["check"])
            assert result.exit_code == 0
            # Check command prints various status messages, not "All checks passed"
            assert "Configuration loaded successfully" in result.stdout

    @patch("pyqt_preview.cli.Config.from_file")
    def test_check_command_config_errors(self, mock_from_file):
        """Test check command with configuration errors."""
        mock_config = Config()
        mock_config.validate = Mock(return_value=["Invalid framework"])
        mock_from_file.return_value = mock_config

        with (
            patch("pyqt_preview.compiler.UICompiler") as mock_compiler_class,
            patch("importlib.util.find_spec") as mock_find_spec,
        ):
            mock_compiler = Mock()
            mock_compiler.check_compiler_available.return_value = True
            mock_compiler_class.return_value = mock_compiler
            mock_find_spec.return_value = True

            result = self.runner.invoke(app, ["check"])
            # Check command shows status but doesn't exit with error code
            # for config issues
            assert result.exit_code == 0
            assert "Configuration issues" in result.stdout

    @patch("pyqt_preview.cli.Config.from_file")
    def test_check_command_compiler_unavailable(self, mock_from_file):
        """Test check command when UI compiler is unavailable."""
        mock_config = Config()
        mock_config.validate = Mock(return_value=[])
        mock_config.detect_framework = Mock(return_value="pyqt6")
        mock_config.get_ui_compiler_command = Mock(return_value="pyuic6")
        mock_from_file.return_value = mock_config

        with (
            patch("pyqt_preview.cli.UICompiler") as mock_compiler_class,
            patch("pyqt_preview.cli.importlib.util.find_spec") as mock_find_spec,
        ):
            mock_compiler = Mock()
            mock_compiler.check_compiler_available.return_value = False
            mock_compiler.get_compiler_version.return_value = None
            mock_compiler_class.return_value = mock_compiler

            # Mock find_spec to return a valid spec (framework is available)
            mock_spec = SimpleNamespace()
            mock_find_spec.return_value = mock_spec

            result = self.runner.invoke(app, ["check"])
            # Check command shows status but doesn't exit with error
            # for unavailable compiler
            assert result.exit_code == 0
            assert "not available" in result.stdout

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        assert callable(main)

    @patch("pyqt_preview.cli.app")
    def test_main_function_calls_typer(self, mock_app):
        """Test that main function calls typer app."""
        main()
        mock_app.assert_called_once()
