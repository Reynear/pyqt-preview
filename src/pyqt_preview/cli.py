"""
Command-line interface for PyQt Preview.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .compiler import UICompiler
from .config import Config
from .core import PreviewEngine

# Initialize rich console for pretty output
console = Console()

# Create the main Typer app
app = typer.Typer(
    name="pyqt-preview",
    help="Live preview tool for PyQt GUI development",
    add_completion=False,
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Display version information."""
    if value:
        console.print(f"[bold cyan]PyQt Preview {__version__}[/bold cyan]")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """PyQt Preview - Live preview tool for PyQt GUI development."""


@app.command()
def run(
    script: str = typer.Argument(help="Python script to preview"),
    watch: Optional[str] = typer.Option(None, "--watch", "-w", help="Directory to watch"),
    ui_dir: Optional[str] = typer.Option(None, "--ui-dir", help="Directory containing .ui files"),
    framework: Optional[str] = typer.Option(None, "--framework", "-f", help="PyQt framework to use"),
    reload_delay: Optional[float] = typer.Option(None, "--reload-delay", help="Delay before reload"),
    preserve_state: Optional[bool] = typer.Option(
        None,
        "--preserve-state/--no-preserve-state",
        help=("Preserve window position and size across reloads (geometry only; does not affect focus)"),
    ),
    keep_window_focus: Optional[bool] = typer.Option(
        None,
        "--keep-window-focus/--no-keep-window-focus",
        help=(
            "Prevent PyQt window from stealing focus on macOS "
            "(restores focus to your editor after reload; does not affect window geometry)"
        ),
    ),
    verbose: Optional[bool] = typer.Option(None, "--verbose", "-v", help="Enable verbose logging"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
) -> None:
    """
    Run a PyQt application with live preview.

    This command starts your PyQt application and watches for file changes,
    automatically reloading the application when .py or .ui files are modified.

    Examples:

        # Basic usage
        pyqt-preview run app.py

        # Watch specific directory
        pyqt-preview run app.py --watch src/

        # Use specific framework
        pyqt-preview run app.py --framework pyqt6

        # Custom reload delay
        pyqt-preview run app.py --reload-delay 1.0
    """

    # Validate script path
    script_path = Path(script)
    if not script_path.exists():
        console.print(f"[red] Script not found: {script}[/red]")
        raise typer.Exit(1)

    if script_path.suffix != ".py":
        console.print(f"[red] Script must be a Python file (.py): {script}[/red]")
        raise typer.Exit(1)

    # Load configuration
    try:
        # Start with file-based config
        config_path = Path(config_file) if config_file else None
        file_config = Config.from_file(config_path)

        # Override with command line arguments
        cli_args = {
            "watch_dir": watch or ".",
            "ui_dir": ui_dir,
            "framework": framework or "auto",
            "reload_delay": reload_delay,
            "preserve_window_state": preserve_state,
            "keep_window_focus": keep_window_focus,
            "verbose": verbose,
        }

        cli_config = Config.from_args(**cli_args)
        config = file_config.merge(cli_config)

    except Exception as e:
        console.print(f"[red] Configuration error: {e}[/red]")
        raise typer.Exit(1) from e

    # Validate configuration
    config_errors = config.validate()
    if config_errors:
        console.print("[red] Configuration errors:[/red]")
        for error in config_errors:
            console.print(f"   [red]• {error}[/red]")
        raise typer.Exit(1)

    # Show startup info
    if not verbose:
        # Show a nice banner
        title = Text("PyQt Preview", style="bold blue")
        subtitle = Text(f"Live reloading for {script_path.name}", style="dim")
        content = Text.assemble(title, "\n", subtitle)

        panel = Panel(
            content,
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)

    # Create and run the preview engine
    try:
        engine = PreviewEngine(str(script_path), config)
        engine.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1) from e


@app.command()
def init(
    directory: Optional[str] = typer.Option(None, "--dir", "-d", help="Directory to initialize (default: current directory)"),
    framework: str = typer.Option(
        "pyqt6",
        "--framework",
        "-f",
        help="GUI framework to use (pyqt5|pyqt6|pyside2|pyside6)",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite existing configuration"),
) -> None:
    """
    Initialize a new PyQt Preview configuration file.

    Creates a .pyqt-preview.toml configuration file in the specified directory
    with sensible defaults for your project.
    """

    target_dir = Path(directory or ".")
    config_file = target_dir / ".pyqt-preview.toml"

    if config_file.exists() and not force:
        console.print(f"[yellow] Configuration file already exists: {config_file}[/yellow]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    # Create configuration content
    config_content = f"""[tool.pyqt-preview]
# GUI framework to use (pyqt5, pyqt6, pyside2, pyside6, auto)
framework = "{framework}"

# UI compiler command (auto, pyuic5, pyuic6, pyside2-uic, pyside6-uic)
ui_compiler = "auto"

# File patterns to watch for changes
watch_patterns = ["*.py", "*.ui"]

# Patterns to ignore
ignore_patterns = ["__pycache__", "*.pyc", "*.pyo", "*.pyd", ".git", ".venv", "venv"]

# Delay before reloading (seconds)
reload_delay = 0.5

# Preserve window position and size across reloads
preserve_window_state = true

# Prevent PyQt window from stealing focus on macOS
keep_window_focus = false

# Enable verbose logging
verbose = false
"""

    try:
        config_file.write_text(config_content)
        console.print(f"[green] Created configuration file: {config_file}[/green]")
        console.print(f"[dim]Framework: {framework}[/dim]")

    except Exception as e:
        console.print(f"[red] Failed to create configuration file: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def check(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
) -> None:
    """
    Check the current configuration and system requirements.

    Validates your configuration file and checks if all required tools
    are available on your system.
    """

    console.print("[bold] PyQt Preview System Check[/bold]\n")

    # Load configuration
    try:
        config_path = Path(config_file) if config_file else None
        config = Config.from_file(config_path)
        console.print("[green] Configuration loaded successfully[/green]")

        # Show configuration
        console.print(f"   Framework: {config.detect_framework()}")
        console.print(f"   Watch directory: {config.watch_dir}")
        console.print(f"   UI directory: {config.ui_dir or 'Same as watch directory'}")
        console.print(f"   Reload delay: {config.reload_delay}s")

    except (OSError, FileNotFoundError) as e:
        console.print(f"[red] Configuration error: {e}[/red]")
        config = Config()  # Use defaults

    # Validate configuration
    config_errors = config.validate()
    if config_errors:
        console.print("\n[red] Configuration issues:[/red]")
        for error in config_errors:
            console.print(f"   [red]• {error}[/red]")
    else:
        console.print("[green] Configuration is valid[/green]")

    # Check framework availability
    console.print(f"\n[bold] Framework Check ({config.detect_framework()})[/bold]")
    framework = config.detect_framework()

    framework_map = {"pyqt5": "PyQt5", "pyqt6": "PyQt6", "pyside2": "PySide2", "pyside6": "PySide6"}

    framework_available = False
    if framework in framework_map:
        framework_available = importlib.util.find_spec(framework_map[framework]) is not None

    if framework_available:
        console.print(f"[green] {framework} is available[/green]")
    else:
        console.print(f"[red] {framework} is not installed[/red]")
        console.print(f"   Install with: pip install {framework}")

    # Check UI compiler

    compiler = UICompiler(config)

    console.print("\n[bold]UI Compiler Check[/bold]")
    if compiler.check_compiler_available():
        compiler_cmd = config.get_ui_compiler_command()
        version = compiler.get_compiler_version()
        console.print(f"[green] {compiler_cmd} is available[/green]")
        if version:
            console.print(f"   Version: {version}")
    else:
        compiler_cmd = config.get_ui_compiler_command()
        console.print(f"[red] {compiler_cmd} is not available[/red]")
        console.print("   .ui files will not be compiled automatically")

    # Check watchdog
    console.print("\n[bold] File Watcher Check[/bold]")
    if importlib.util.find_spec("watchdog") is not None:
        console.print("[green] watchdog is available[/green]")
    else:
        console.print("[red] watchdog is not installed[/red]")
        console.print("   Install with: pip install watchdog")

    console.print("\n[bold] System Summary[/bold]")
    console.print(f"Python: {sys.version}")
    console.print(f"Platform: {sys.platform}")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
