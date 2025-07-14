"""
Core preview engine for PyQt Preview development tool.

Manages the lifecycle of PyQt applications with simple live reloading.
"""

import atexit
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from .compiler import UICompiler
from .config import Config
from .logging_config import get_logger, setup_logging
from .security import SecurityError, validate_python_file
from .watcher import FileWatcher

logger = get_logger(__name__)


class WindowState:
    """Manages window position and size state across reloads."""

    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file or Path(tempfile.gettempdir()) / "pyqt_preview_state.json"
        self.state: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load window state from file."""
        try:
            if self.state_file.exists():
                with self.state_file.open(encoding="utf-8") as f:
                    self.state = json.loads(f.read())
                logger.debug(f"Loaded window state from {self.state_file}")
        except (OSError, json.JSONDecodeError) as e:
            logger.debug(f"Could not load window state: {e}")
            self.state = {}

    def save(self, geometry: Optional[tuple[int, int, int, int]] = None) -> None:
        """Save window state to file."""
        try:
            if geometry:
                self.state["geometry"] = geometry

            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with self.state_file.open("w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
            logger.debug(f"Saved window state to {self.state_file}")
        except OSError as e:
            logger.debug(f"Could not save window state: {e}")

    def get_geometry(self) -> Optional[tuple[int, int, int, int]]:
        """Get saved window geometry (x, y, width, height)."""
        geometry = self.state.get("geometry")
        if geometry and isinstance(geometry, (list, tuple)) and len(geometry) == 4:
            return tuple(geometry)
        return None

    def cleanup(self) -> None:
        """Clean up state file."""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
        except OSError as e:
            logger.debug(f"Could not remove state file: {e}")


class PreviewProcess:
    """Manages a PyQt application process."""

    def __init__(self, script_path: str, config: Config, window_state: WindowState):
        self.config = config
        self.window_state = window_state
        self.process: Optional[subprocess.Popen[bytes]] = None

        # Validate script path
        try:
            self.script_path = validate_python_file(script_path)
        except SecurityError as e:
            logger.error(f"Invalid script: {e}")
            raise

    def start(self) -> bool:
        """Start the PyQt application process."""
        if self.process and self.process.poll() is None:
            return True

        try:
            # Build command to run the script
            cmd = [sys.executable, str(self.script_path)]

            # Set up environment
            env = os.environ.copy()

            # Add geometry restoration if enabled
            if self.config.preserve_window_state:
                geometry = self.window_state.get_geometry()
                if geometry:
                    env["PYQT_PREVIEW_GEOMETRY"] = f"{geometry[0]},{geometry[1]},{geometry[2]},{geometry[3]}"

            # Pass keep window focus flag to subprocess if set and on macOS
            if getattr(self.config, "keep_window_focus", False) and sys.platform == "darwin":
                env["PYQT_PREVIEW_KEEP_FOCUS"] = "1"

            logger.info(f"Starting application: {self.script_path}")

            # Start process
            # Safe: cmd is constructed from validated script path and sys.executable
            self.process = subprocess.Popen(cmd, cwd=self.script_path.parent, env=env)  # nosec

            # Optionally restore focus to previous app on macOS if keep_window_focus is set
            if getattr(self.config, "keep_window_focus", False) and sys.platform == "darwin":
                try:
                    # This AppleScript restores focus to the previously active app
                    applescript = """
                    tell application "System Events"
                        set frontApp to name of first application process whose frontmost is true
                    end tell
                    delay 0.2
                    tell application frontApp to activate
                    """
                    # Safe: osascript is a system binary, not user-supplied
                    subprocess.Popen(["osascript", "-e", applescript])  # nosec
                except (OSError, subprocess.SubprocessError) as e:
                    logger.debug(f"Could not restore focus to previous app: {e}")

            logger.info(f"Process started (PID: {self.process.pid})")
            return True

        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Failed to start application: {e}")
            return False

    def restart(self) -> bool:
        """Restart the application process."""
        if self.process:
            self.stop()
        return self.start()

    def stop(self) -> None:
        """Stop the application process."""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except (OSError, subprocess.SubprocessError) as e:
                logger.error(f"Error stopping process: {e}")

    def is_running(self) -> bool:
        """Check if the process is running."""
        return self.process is not None and self.process.poll() is None


class PreviewEngine:
    """Main engine for PyQt Preview live reload functionality."""

    def __init__(self, script_path: str, config: Config):
        self.script_path = script_path
        self.config = config
        self.window_state = WindowState()
        self.reload_count = 0
        self.is_running = False

        # Set up logging
        setup_logging(verbose=config.verbose)

        # Initialize components
        self.watcher = FileWatcher(config, self._on_file_change)
        self.compiler = UICompiler(config)
        self.process = PreviewProcess(script_path, config, self.window_state)

        # Register cleanup
        atexit.register(self.cleanup)

    def _on_file_change(self, changed_file: str) -> None:
        """Handle file change events."""
        logger.info(f"File changed: {changed_file}")

        try:
            # Handle UI compilation
            if changed_file.endswith(".ui"):
                result = self.compiler.handle_file_change(changed_file)
                if result:
                    logger.info(result)

            # Restart application
            if self.process.restart():
                self.reload_count += 1
                logger.info(f"Reload #{self.reload_count} completed")
            else:
                logger.error("Failed to restart application")

        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Error handling file change: {e}")

    def start(self) -> bool:
        """Start the preview engine."""
        if self.is_running:
            return True

        try:
            logger.info("Starting PyQt Preview...")

            # Start file watcher
            self.watcher.start()

            # Start initial application
            if not self.process.start():
                logger.error("Failed to start initial application")
                return False

            self.is_running = True
            logger.info("PyQt Preview started successfully")
            return True

        except (OSError, SecurityError) as e:
            logger.error(f"Failed to start preview engine: {e}")
            return False

    def stop(self) -> None:
        """Stop the preview engine."""
        if not self.is_running:
            return

        logger.info("Stopping PyQt Preview...")

        try:
            # Stop file watcher
            if self.watcher is not None:
                self.watcher.stop()

            # Stop application process
            if self.process is not None:
                self.process.stop()

            self.is_running = False
            logger.info("PyQt Preview stopped")

        except OSError as e:
            logger.error(f"Error stopping preview engine: {e}")

    def run(self) -> None:
        """Run the preview engine (blocking)."""
        if not self.start():
            return

        try:
            while self.is_running and self.process.is_running():
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        if self.window_state is not None:
            self.window_state.cleanup()
