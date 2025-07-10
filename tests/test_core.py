"""
Comprehensive tests for PyQt Preview core module.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pyqt_preview.config import Config
from pyqt_preview.core import PreviewEngine, PreviewProcess, WindowState
from pyqt_preview.security import SecurityError


class TestWindowState:
    """Test cases for WindowState class."""

    def test_window_state_initialization(self):
        """Test WindowState initialization."""
        state = WindowState()
        assert isinstance(state.state_file, Path)
        assert state.state == {}

    def test_window_state_initialization_with_file(self):
        """Test WindowState initialization with custom file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            state_file = Path(f.name)

        try:
            state = WindowState(state_file)
            assert state.state_file == state_file
        finally:
            state_file.unlink(missing_ok=True)

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent state file."""
        with tempfile.NamedTemporaryFile(delete=True) as f:
            state_file = Path(f.name)

        # File should not exist now
        state = WindowState(state_file)
        assert state.state == {}

    def test_load_existing_valid_file(self):
        """Test loading from existing valid state file."""
        test_state = {"geometry": [100, 200, 800, 600]}

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(test_state, f)
            state_file = Path(f.name)

        try:
            state = WindowState(state_file)
            assert state.state == test_state
        finally:
            state_file.unlink()

    def test_load_invalid_json_file(self):
        """Test loading from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write("invalid json {")
            state_file = Path(f.name)

        try:
            state = WindowState(state_file)
            assert state.state == {}  # Should default to empty
        finally:
            state_file.unlink()

    def test_save_without_geometry(self):
        """Test saving state without geometry."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            state_file = Path(f.name)

        try:
            state = WindowState(state_file)
            state.state = {"test": "value"}
            state.save()

            # Reload and verify
            with open(state_file) as f:
                saved_state = json.load(f)
            assert saved_state == {"test": "value"}
        finally:
            state_file.unlink()

    def test_save_with_geometry(self):
        """Test saving state with geometry."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            state_file = Path(f.name)

        try:
            state = WindowState(state_file)
            geometry = (100, 200, 800, 600)
            state.save(geometry)

            # Reload and verify
            with open(state_file) as f:
                saved_state = json.load(f)
            assert saved_state["geometry"] == list(geometry)
        finally:
            state_file.unlink()

    def test_save_creates_directory(self):
        """Test that save creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "subdir" / "state.json"

            state = WindowState(state_file)
            state.save((0, 0, 100, 100))

            assert state_file.exists()
            assert state_file.parent.exists()

    def test_get_geometry_valid(self):
        """Test getting valid geometry."""
        state = WindowState()
        state.state = {"geometry": [100, 200, 800, 600]}

        geometry = state.get_geometry()
        assert geometry == (100, 200, 800, 600)

    def test_get_geometry_invalid_format(self):
        """Test getting geometry with invalid format."""
        test_cases = [
            {"geometry": "invalid"},
            {"geometry": [100, 200]},  # Wrong length
            {"geometry": [100, 200, 800, 600, 900]},  # Wrong length
            {},  # No geometry key
        ]

        for test_state in test_cases:
            state = WindowState()
            state.state = test_state
            assert state.get_geometry() is None

    def test_cleanup(self):
        """Test cleanup removes state file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            state_file = Path(f.name)

        assert state_file.exists()

        state = WindowState(state_file)
        state.cleanup()

        assert not state_file.exists()

    def test_cleanup_nonexistent_file(self):
        """Test cleanup with nonexistent file doesn't raise error."""
        with tempfile.NamedTemporaryFile(delete=True) as f:
            state_file = Path(f.name)

        # File should not exist now
        state = WindowState(state_file)
        state.cleanup()  # Should not raise


class TestPreviewProcess:
    """Test cases for PreviewProcess class."""

    def test_preview_process_initialization_valid_script(self):
        """Test PreviewProcess initialization with valid script."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            assert process.script_path == Path(script_path).resolve()
            assert process.config == config
            assert process.window_state == window_state
            assert process.process is None
        finally:
            Path(script_path).unlink()

    def test_preview_process_initialization_invalid_script(self):
        """Test PreviewProcess initialization with invalid script."""
        config = Config()
        window_state = WindowState()

        with pytest.raises(SecurityError):
            PreviewProcess("/nonexistent/script.py", config, window_state)

    @patch("subprocess.Popen")
    def test_start_process_success(self, mock_popen):
        """Test successful process start."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process

            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            result = process.start()

            assert result is True
            assert process.process == mock_process
            mock_popen.assert_called_once()
        finally:
            Path(script_path).unlink()

    @patch("subprocess.Popen")
    def test_start_process_with_geometry(self, mock_popen):
        """Test process start with window geometry."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            mock_process = Mock()
            mock_popen.return_value = mock_process

            config = Config(preserve_window_state=True)
            window_state = WindowState()
            window_state.state = {"geometry": [100, 200, 800, 600]}

            process = PreviewProcess(script_path, config, window_state)
            process.start()

            # Check that environment was set
            call_args = mock_popen.call_args
            env = call_args[1]["env"]
            assert "PYQT_PREVIEW_GEOMETRY" in env
            assert env["PYQT_PREVIEW_GEOMETRY"] == "100,200,800,600"
        finally:
            Path(script_path).unlink()

    def test_start_already_running(self):
        """Test starting when process is already running."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            # Mock running process
            mock_process = Mock()
            mock_process.poll.return_value = None  # Still running
            process.process = mock_process

            result = process.start()
            assert result is True
        finally:
            Path(script_path).unlink()

    @patch("subprocess.Popen")
    def test_start_process_exception(self, mock_popen):
        """Test process start with exception."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            mock_popen.side_effect = OSError("Failed to start")

            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            result = process.start()
            assert result is False
        finally:
            Path(script_path).unlink()

    def test_restart_calls_stop_then_start(self):
        """Test restart calls stop then start."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            with (
                patch.object(process, "stop") as mock_stop,
                patch.object(process, "start") as mock_start,
            ):
                mock_start.return_value = True

                # Set up existing process
                process.process = Mock()

                result = process.restart()

                mock_stop.assert_called_once()
                mock_start.assert_called_once()
                assert result is True
        finally:
            Path(script_path).unlink()

    def test_stop_process_graceful(self):
        """Test graceful process stop."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            # Mock running process
            mock_process = Mock()
            mock_process.poll.return_value = None  # Still running
            process.process = mock_process

            process.stop()

            mock_process.terminate.assert_called_once()
            mock_process.wait.assert_called_once_with(timeout=5)
        finally:
            Path(script_path).unlink()

    def test_stop_process_force_kill(self):
        """Test force kill when graceful stop fails."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            # Mock process that times out on terminate
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_process.wait.side_effect = [
                subprocess.TimeoutExpired(["test"], 5),
                None,
            ]
            process.process = mock_process

            process.stop()

            mock_process.terminate.assert_called_once()
            mock_process.kill.assert_called_once()
            assert mock_process.wait.call_count == 2
        finally:
            Path(script_path).unlink()

    def test_is_running_true(self):
        """Test is_running returns True for running process."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            mock_process = Mock()
            mock_process.poll.return_value = None  # Still running
            process.process = mock_process

            assert process.is_running() is True
        finally:
            Path(script_path).unlink()

    def test_is_running_false(self):
        """Test is_running returns False for stopped process."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            window_state = WindowState()
            process = PreviewProcess(script_path, config, window_state)

            # No process
            assert process.is_running() is False

            # Finished process
            mock_process = Mock()
            mock_process.poll.return_value = 0  # Finished
            process.process = mock_process

            assert process.is_running() is False
        finally:
            Path(script_path).unlink()


class TestPreviewEngine:
    """Test cases for PreviewEngine class."""

    def test_preview_engine_initialization(self):
        """Test PreviewEngine initialization."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            assert engine.script_path == script_path
            assert engine.config == config
            assert engine.reload_count == 0
            assert engine.is_running is False
            assert engine.watcher is not None
            assert engine.compiler is not None
            assert engine.process is not None
        finally:
            Path(script_path).unlink()

    @patch("pyqt_preview.core.setup_logging")
    def test_preview_engine_sets_up_logging(self, mock_setup_logging):
        """Test that PreviewEngine sets up logging."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config(verbose=True)
            PreviewEngine(script_path, config)

            mock_setup_logging.assert_called_once_with(verbose=True)
        finally:
            Path(script_path).unlink()

    def test_on_file_change_python_file(self):
        """Test file change handling for Python files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock process restart
            engine.process.restart = Mock(return_value=True)

            engine._on_file_change("test.py")

            assert engine.reload_count == 1
            engine.process.restart.assert_called_once()
        finally:
            Path(script_path).unlink()

    def test_on_file_change_ui_file(self):
        """Test file change handling for UI files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock compiler and process
            engine.compiler.handle_file_change = Mock(return_value="Compiled successfully")
            engine.process.restart = Mock(return_value=True)

            engine._on_file_change("test.ui")

            engine.compiler.handle_file_change.assert_called_once_with("test.ui")
            engine.process.restart.assert_called_once()
            assert engine.reload_count == 1
        finally:
            Path(script_path).unlink()

    def test_on_file_change_process_restart_failure(self):
        """Test file change when process restart fails."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock process restart failure
            engine.process.restart = Mock(return_value=False)

            engine._on_file_change("test.py")

            # Should not increment reload count on failure
            assert engine.reload_count == 0
        finally:
            Path(script_path).unlink()

    def test_on_file_change_exception(self):
        """Test file change handling with exception."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock process restart to raise exception
            engine.process.restart = Mock(side_effect=OSError("Test error"))

            # Should not raise exception
            engine._on_file_change("test.py")

            assert engine.reload_count == 0
        finally:
            Path(script_path).unlink()

    def test_start_already_running(self):
        """Test start when already running."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)
            engine.is_running = True

            result = engine.start()
            assert result is True
        finally:
            Path(script_path).unlink()

    def test_start_success(self):
        """Test successful start."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock components
            engine.watcher.start = Mock()
            engine.process.start = Mock(return_value=True)

            result = engine.start()

            assert result is True
            assert engine.is_running is True
            engine.watcher.start.assert_called_once()
            engine.process.start.assert_called_once()
        finally:
            Path(script_path).unlink()

    def test_start_process_failure(self):
        """Test start with process failure."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock process failure
            engine.watcher.start = Mock()
            engine.process.start = Mock(return_value=False)

            result = engine.start()

            assert result is False
            assert engine.is_running is False
        finally:
            Path(script_path).unlink()

    def test_stop(self):
        """Test stop functionality."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)
            engine.is_running = True

            # Mock components
            engine.watcher.stop = Mock()
            engine.process.stop = Mock()

            engine.stop()

            assert engine.is_running is False
            engine.watcher.stop.assert_called_once()
            engine.process.stop.assert_called_once()
        finally:
            Path(script_path).unlink()

    def test_cleanup(self):
        """Test cleanup functionality."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock components
            engine.stop = Mock()
            engine.window_state.cleanup = Mock()

            engine.cleanup()

            engine.stop.assert_called_once()
            engine.window_state.cleanup.assert_called_once()
        finally:
            Path(script_path).unlink()

    @patch("builtins.input", return_value="")  # Mock input for run loop
    def test_run_calls_start_and_waits(self, mock_input):
        """Test run calls start and waits for input."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock start
            engine.start = Mock(return_value=True)

            engine.run()

            engine.start.assert_called_once()
        finally:
            Path(script_path).unlink()

    def test_run_start_failure(self):
        """Test run with start failure."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            script_path = f.name

        try:
            config = Config()
            engine = PreviewEngine(script_path, config)

            # Mock start failure
            engine.start = Mock(return_value=False)

            # run() method returns early when start() fails, doesn't raise exception
            engine.run()

            # Verify start was called once
            engine.start.assert_called_once()
        finally:
            Path(script_path).unlink()
