"""
UI compiler for PyQt Preview.

Handles compilation of .ui files to .py files using appropriate tools.
"""

import subprocess
from pathlib import Path
from typing import Optional

from .config import Config


class UICompiler:
    """Handles compilation of Qt Designer .ui files to Python code."""

    def __init__(self, config: Config):
        self.config = config

    def find_ui_files(self, directory: Optional[str] = None) -> list[Path]:
        """Find all .ui files in the specified directory."""
        search_dir = Path(directory or self.config.ui_dir or self.config.watch_dir)

        if not search_dir.exists():
            return []

        ui_files: list[Path] = []
        for pattern in ["*.ui"]:
            ui_files.extend(search_dir.rglob(pattern))

        return sorted(ui_files)

    def get_output_path(self, ui_file: Path) -> Path:
        """Get the output .py file path for a .ui file."""
        if self.config.output_dir:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            # Use the same filename but with .py extension
            return output_dir / f"{ui_file.stem}.py"
        # Output in the same directory as the .ui file
        return ui_file.parent / f"{ui_file.stem}.py"

    def compile_ui_file(self, ui_file: Path) -> tuple[bool, str]:
        """
        Compile a single .ui file to Python code.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            output_file = self.get_output_path(ui_file)
            compiler_cmd = self.config.get_ui_compiler_command()

            # Build the command
            cmd = [compiler_cmd, str(ui_file), "-o", str(output_file)]

            if self.config.verbose:
                print(f" Compiling {ui_file.name} -> {output_file.name}")
                print(f" Command: {' '.join(cmd)}")

            # Run the compiler
            # Safe: cmd is constructed from validated config, not user input
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)  # nosec

            if result.returncode == 0:
                return True, f"Successfully compiled {ui_file.name}"
            return False, f"Compilation failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, f"Compilation timeout for {ui_file.name}"
        except subprocess.CalledProcessError as e:
            return False, f"Compilation error: {e.stderr}"
        except FileNotFoundError:
            compiler_cmd = self.config.get_ui_compiler_command()
            return (
                False,
                f"UI compiler '{compiler_cmd}' not found. Please install the appropriate Qt tools.",
            )
        except OSError as e:
            return False, f"Unexpected error: {e!s}"

    def compile_all_ui_files(self, directory: Optional[str] = None) -> tuple[int, int, list[str]]:
        """
        Compile all .ui files in the specified directory.

        Returns:
            Tuple of (successful_count, total_count, error_messages)
        """
        ui_files = self.find_ui_files(directory)

        if not ui_files:
            return 0, 0, []

        successful = 0
        errors = []

        for ui_file in ui_files:
            success, message = self.compile_ui_file(ui_file)
            if success:
                successful += 1
            else:
                errors.append(f"{ui_file.name}: {message}")

        return successful, len(ui_files), errors

    def is_ui_file_newer(self, ui_file: Path) -> bool:
        """Check if .ui file is newer than its corresponding .py file."""
        py_file = self.get_output_path(ui_file)

        if not py_file.exists():
            return True

        ui_mtime = ui_file.stat().st_mtime
        py_mtime = py_file.stat().st_mtime

        return ui_mtime > py_mtime

    def compile_if_needed(self, ui_file: Path) -> tuple[bool, str]:
        """Compile .ui file only if it's newer than the .py file."""
        if not self.is_ui_file_newer(ui_file):
            return True, f"{ui_file.name} is up to date"

        return self.compile_ui_file(ui_file)

    def get_compiler_version(self) -> Optional[str]:
        """Get the version of the UI compiler."""
        try:
            compiler_cmd = self.config.get_ui_compiler_command()
            # Safe: compiler_cmd is determined by config, not user input
            result = subprocess.run(
                [compiler_cmd, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )  # nosec

            if result.returncode == 0:
                return result.stdout.strip()
            return None

        except (OSError, subprocess.SubprocessError):
            return None

    def check_compiler_available(self) -> bool:
        """Check if the UI compiler is available."""
        try:
            compiler_cmd = self.config.get_ui_compiler_command()
            # Safe: compiler_cmd is determined by config, not user input
            result = subprocess.run(
                [compiler_cmd, "--help"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )  # nosec
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    def handle_file_change(self, changed_file: str) -> bool:
        """
        Handle a file change event, compiling .ui files if needed.

        Returns:
            True if any compilation was performed
        """
        file_path = Path(changed_file)

        # If it's a .ui file, compile it
        if file_path.suffix == ".ui":
            success, message = self.compile_ui_file(file_path)
            if self.config.verbose:
                status = "OK" if success else "FAIL"
                print(f"[{status}] {message}")
            return success

        # If it's a .py file, check if there are any .ui files that need recompiling
        if file_path.suffix == ".py":
            ui_files = self.find_ui_files()
            compiled_any = False

            for ui_file in ui_files:
                if self.is_ui_file_newer(ui_file):
                    success, message = self.compile_ui_file(ui_file)
                    if success:
                        compiled_any = True
                    if self.config.verbose:
                        status = "OK" if success else "FAIL"
                        print(f"[{status}] {message}")

            return compiled_any

        return False
