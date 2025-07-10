"""
File watcher for PyQt Preview.

Monitors filesystem changes and triggers application reloads.
"""

import fnmatch
import time
from pathlib import Path
from typing import Any, Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .config import Config


class PreviewFileHandler(FileSystemEventHandler):
    """File system event handler for preview reloading."""

    def __init__(
        self,
        config: Config,
        on_change_callback: Callable[[str], None],
    ):
        super().__init__()
        self.config = config
        self.on_change_callback = on_change_callback
        self._last_reload_time = 0.0
        self._pending_files: set[str] = set()

    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored based on patterns."""
        path = Path(file_path)

        # Check ignore patterns against various parts of the path
        for pattern in self.config.ignore_patterns:
            # Check against full path
            if fnmatch.fnmatch(str(path), pattern):
                return True
            # Check against filename
            if fnmatch.fnmatch(path.name, pattern):
                return True
            # Check if any part in the path matches the pattern
            for part in path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True

        # Check if file matches watch patterns
        matches_pattern = False
        for pattern in self.config.watch_patterns:
            if fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern):
                matches_pattern = True
                break

        return not matches_pattern

    def _should_reload(self) -> bool:
        """Check if enough time has passed since last reload."""
        current_time = time.time()
        if current_time - self._last_reload_time >= self.config.reload_delay:
            self._last_reload_time = current_time
            return True
        return False

    def on_modified(self, event: Any) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = str(event.src_path)  # Ensure it's a string

        if self._should_ignore_file(file_path):
            return

        self._pending_files.add(file_path)

        if self._should_reload():
            self._trigger_reload()

    def on_created(self, event: Any) -> None:
        """Handle file creation events."""
        self.on_modified(event)

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move events."""
        if event.is_directory:
            return

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if event.is_directory:
            return

    def _trigger_reload(self) -> None:
        """Trigger the reload callback with pending files."""
        if self._pending_files:
            files = list(self._pending_files)
            self._pending_files.clear()

            if self.config.verbose:
                print(f"Reloading due to changes in: {', '.join(files)}")

            # Call the callback with the first changed file (main trigger)
            self.on_change_callback(files[0])


class FileWatcher:
    """Main file watcher class."""

    def __init__(self, config: Config, on_change_callback: Callable[[str], None]):
        self.config = config
        self.on_change_callback = on_change_callback
        self.observer: Optional[Any] = None
        self.handler: Optional[PreviewFileHandler] = None
        self._is_running = False

    def start(self) -> None:
        """Start watching for file changes."""
        if self._is_running:
            return

        self.handler = PreviewFileHandler(self.config, self.on_change_callback)
        self.observer = Observer()

        watch_path = Path(self.config.watch_dir).resolve()

        if not watch_path.exists():
            raise FileNotFoundError(f"Watch directory does not exist: {watch_path}")

        self.observer.schedule(self.handler, str(watch_path), recursive=True)

        self.observer.start()
        self._is_running = True

        if self.config.verbose:
            print(f"Watching for changes in: {watch_path}")
            print(f"Watch patterns: {', '.join(self.config.watch_patterns)}")
            print(f"Ignore patterns: {', '.join(self.config.ignore_patterns)}")

    def stop(self) -> None:
        """Stop watching for file changes."""
        if not self._is_running or not self.observer:
            return

        self.observer.stop()
        self.observer.join(timeout=1.0)
        self._is_running = False

        if self.config.verbose:
            print("File watcher stopped")

    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._is_running

    def __enter__(self) -> "FileWatcher":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()
