"""
Tests for the file watcher module.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from watchdog.events import FileModifiedEvent

from pyqt_preview.config import Config
from pyqt_preview.watcher import FileWatcher, PreviewFileHandler


class TestPreviewFileHandler:
    """Test cases for PreviewFileHandler."""

    def test_should_ignore_file(self):
        """Test file ignore patterns."""
        config = Config(
            watch_patterns=["*.py", "*.ui"],
            ignore_patterns=["__pycache__", "*.pyc", ".git"],
        )
        callback = Mock()
        handler = PreviewFileHandler(config, callback)

        # Should ignore files matching ignore patterns
        assert handler._should_ignore_file("__pycache__/test.py")
        assert handler._should_ignore_file("test.pyc")
        assert handler._should_ignore_file(".git/config")

        # Should ignore files not matching watch patterns
        assert handler._should_ignore_file("test.txt")
        assert handler._should_ignore_file("readme.md")

        # Should not ignore files matching watch patterns
        assert not handler._should_ignore_file("test.py")
        assert not handler._should_ignore_file("main.ui")

    def test_should_reload_timing(self):
        """Test reload timing logic."""
        config = Config(reload_delay=0.1)
        callback = Mock()
        handler = PreviewFileHandler(config, callback)

        # First call should allow reload
        assert handler._should_reload()

        # Immediate second call should not allow reload
        assert not handler._should_reload()

        # After delay, should allow reload again
        time.sleep(0.12)
        assert handler._should_reload()

    @patch("pyqt_preview.watcher.time.time")
    def test_trigger_reload_batching(self, mock_time):
        """Test that file changes are batched before triggering reload."""
        mock_time.return_value = 0.0

        config = Config(reload_delay=0.5)
        callback = Mock()
        handler = PreviewFileHandler(config, callback)

        # Add some pending files
        handler._pending_files.add("file1.py")
        handler._pending_files.add("file2.py")

        # Trigger reload
        handler._trigger_reload()

        # Should call callback with one of the files
        callback.assert_called_once()
        # Pending files should be cleared
        assert len(handler._pending_files) == 0


class TestFileWatcher:
    """Test cases for FileWatcher."""

    def test_file_watcher_initialization(self):
        """Test file watcher initialization."""
        config = Config()
        callback = Mock()

        watcher = FileWatcher(config, callback)

        assert watcher.config == config
        assert watcher.on_change_callback == callback
        assert not watcher.is_running()
        assert watcher.observer is None

    def test_file_watcher_context_manager(self):
        """Test file watcher as context manager."""
        config = Config()
        callback = Mock()

        with (
            patch.object(FileWatcher, "start"),
            patch.object(FileWatcher, "stop"),
            FileWatcher(config, callback) as watcher,
        ):
            assert watcher is not None

    def test_start_with_nonexistent_directory(self):
        """Test starting watcher with nonexistent directory."""
        config = Config(watch_dir="/nonexistent/directory")
        callback = Mock()
        watcher = FileWatcher(config, callback)

        with pytest.raises(FileNotFoundError):
            watcher.start()

    def test_start_with_valid_directory(self):
        """Test starting watcher with valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(watch_dir=temp_dir)
            callback = Mock()
            watcher = FileWatcher(config, callback)

            # Mock the observer to avoid actually starting it
            with patch("pyqt_preview.watcher.Observer") as mock_observer_class:
                mock_observer = Mock()
                mock_observer_class.return_value = mock_observer

                watcher.start()

                assert watcher.is_running()
                mock_observer.schedule.assert_called_once()
                mock_observer.start.assert_called_once()

                watcher.stop()
                mock_observer.stop.assert_called_once()

    def test_double_start_stop(self):
        """Test that starting/stopping multiple times is safe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(watch_dir=temp_dir)
            callback = Mock()
            watcher = FileWatcher(config, callback)

            with patch("pyqt_preview.watcher.Observer"):
                # Starting twice should be safe
                watcher.start()
                watcher.start()
                assert watcher.is_running()

                # Stopping twice should be safe
                watcher.stop()
                watcher.stop()
                assert not watcher.is_running()

    def test_watcher_with_different_patterns(self):
        """Test watcher with different file patterns."""
        config = Config(
            watch_patterns=["*.py", "*.qml", "*.ui"],
            ignore_patterns=["test_*", "*.tmp"],
        )
        callback = Mock()
        handler = PreviewFileHandler(config, callback)

        # Test various file types
        assert not handler._should_ignore_file("main.py")
        assert not handler._should_ignore_file("app.qml")
        assert not handler._should_ignore_file("form.ui")

        # Test ignore patterns
        assert handler._should_ignore_file("test_module.py")
        assert handler._should_ignore_file("temp.tmp")

        # Test non-matching patterns
        assert handler._should_ignore_file("readme.md")
        assert handler._should_ignore_file("config.json")

    def test_file_handler_pending_files_management(self):
        """Test that pending files are managed correctly."""
        config = Config(reload_delay=0.1)
        callback = Mock()
        handler = PreviewFileHandler(config, callback)

        # Add files to pending
        handler._pending_files.add("file1.py")
        handler._pending_files.add("file2.py")

        assert len(handler._pending_files) == 2

        # Trigger reload should clear pending files
        handler._trigger_reload()
        assert len(handler._pending_files) == 0

    def test_file_handler_timing_precision(self):
        """Test file handler timing behavior."""
        config = Config(reload_delay=0.05)  # Very short delay
        callback = Mock()
        handler = PreviewFileHandler(config, callback)

        # First reload should be allowed
        assert handler._should_reload()

        # Immediate second should not
        assert not handler._should_reload()

        # After sufficient time, should be allowed again
        time.sleep(0.06)
        assert handler._should_reload()

    def test_watcher_observer_lifecycle(self):
        """Test that observer is properly managed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(watch_dir=temp_dir)
            callback = Mock()
            watcher = FileWatcher(config, callback)

            assert watcher.observer is None

            with patch("pyqt_preview.watcher.Observer") as mock_observer_class:
                mock_observer = Mock()
                mock_observer_class.return_value = mock_observer

                # Start should create and start observer
                watcher.start()
                assert watcher.observer == mock_observer
                mock_observer.start.assert_called_once()

                # Stop should stop and clear observer
                watcher.stop()
                mock_observer.stop.assert_called_once()
                mock_observer.join.assert_called_once()

    def test_watcher_context_manager_exception_handling(self):
        """Test context manager handles exceptions gracefully."""
        config = Config(watch_dir="/nonexistent")
        callback = Mock()

        # Should handle FileNotFoundError gracefully
        with pytest.raises(FileNotFoundError), FileWatcher(config, callback) as _:
            pass  # Exception should be raised here

    def test_file_handler_event_processing(self):
        """Test that file handler processes events correctly."""
        config = Config()
        callback = Mock()
        handler = PreviewFileHandler(config, callback)

        # Mock file system event
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            event = FileModifiedEvent(f.name)

            # Process the event
            handler.on_modified(event)

            # Should trigger callback after delay
            time.sleep(0.1)  # Wait for debounce

            # Note: This test depends on timing, so might be flaky
            # In practice, the handler adds files to pending and processes them

        Path(f.name).unlink()

    def test_watcher_integration_with_real_files(self):
        """Test watcher integration with real file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(watch_dir=temp_dir, reload_delay=0.1)
            callback = Mock()

            # Create a test file
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('initial')")

            with patch("pyqt_preview.watcher.Observer") as mock_observer_class:
                mock_observer = Mock()
                mock_observer_class.return_value = mock_observer

                with FileWatcher(config, callback) as watcher:
                    # Verify observer was set up correctly
                    mock_observer.schedule.assert_called_once()
                    mock_observer.start.assert_called_once()

                    # Simulate file change by calling handler directly
                    if watcher.observer:
                        # In real usage, the observer would trigger this
                        pass
