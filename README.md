# PyQt Preview - Live Preview Tool for PyQt GUI Development

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/your-username/pyqt-preview)

PyQt Preview is a development tool for PyQt5/PyQt6/PySide2/PySide6 GUI applications that provides live reloading when editing `.py` or `.ui` files—speeding up your development process. It works out of the box, is highly configurable, and supports advanced workflows for both beginners and professionals.

## Features

- **Live Reload**: Instantly reloads your PyQt application when files change
- **UI Compilation**: Automatically compiles .ui files to Python code
- **Multiple Frameworks**: Supports PyQt5, PyQt6, PySide2, and PySide6
- **Smart Watching**: Configurable file patterns and ignore rules
- **Zero Configuration**: Works out of the box with sensible defaults
- **Preserve State**: Maintains window position and size across reloads
- **Flexible Config**: TOML-based configuration with CLI overrides
- **Verbose Logging**: Optional detailed output for debugging

## Quick Start

### Installation

```bash
pip install pyqt-preview
```

### Basic Usage

```bash
# Preview a single PyQt application
pyqt-preview run app.py

# Watch a directory for changes
pyqt-preview run app.py --watch src/

# Specify UI files directory
pyqt-preview run app.py --watch . --ui-dir ui/

# Use with PySide instead of PyQt
pyqt-preview run app.py --framework pyside6
```

### Requirements
- Python 3.8+
- PyQt5/PyQt6 or PySide2/PySide6
- watchdog
- For .ui file compilation: `pyuic6`, `pyuic5`, `pyside6-uic`, or `pyside2-uic` (install via PyQt/PySide tools)

## How It Works

PyQt Preview watches your project files for changes, recompiles UI files if needed, and restarts your application automatically. Window geometry and focus can be preserved (see platform notes below).

## Configuration

Create a `.pyqt-preview.toml` file in your project root for custom settings:

```toml
[tool.pyqt-preview]
framework = "pyqt6"  # pyqt5, pyqt6, pyside2, pyside6
watch_patterns = ["*.py", "*.ui"]
ignore_patterns = ["__pycache__", "*.pyc"]
ui_compiler = "auto"  # auto, pyuic5, pyuic6, pyside2-uic, pyside6-uic
preserve_window_state = true
reload_delay = 0.5  # seconds
verbose = true
```

- **CLI flags always override config file and defaults.**
- See `pyqt-preview --help` for all options.

## Examples

See the `examples/` directory for working applications:
- `simple_app.py`: Basic PyQt6 app
- `simple_pyqt5.py`: PyQt5 compatibility
- `ui_app.py` + `demo.ui`: Qt Designer integration

## CLI Commands

### `run` Command

Start a PyQt application with live preview.

```bash
pyqt-preview run SCRIPT [OPTIONS]

Arguments:
  SCRIPT  Path to the Python script to run

Options:
  --watch PATH          Directory to watch for changes [default: .]
  --ui-dir PATH         Directory containing .ui files
  --framework TEXT      GUI framework (pyqt5|pyqt6|pyside2|pyside6)
  --reload-delay FLOAT  Delay before reload in seconds [default: 0.5]
  --preserve-state      Preserve window position and size
  --keep-window-focus   Prevent PyQt window from stealing focus on macOS
  --config PATH         Path to configuration file
  --verbose             Enable verbose logging
  --help                Show this message and exit
```

### `init` Command

Initialize a new PyQt Preview configuration file.

```bash
pyqt-preview init [OPTIONS]

Options:
  --dir PATH           Directory to initialize [default: current directory]
  --framework TEXT     GUI framework (pyqt5|pyqt6|pyside2|pyside6) [default: pyqt6]
  --force              Overwrite existing configuration
  --help               Show this message and exit
```

### `check` Command

Check the current configuration and system requirements.

```bash
pyqt-preview check [OPTIONS]

Options:
  --config PATH        Path to configuration file
  --help              Show this message and exit
```

### Global Options

```bash
pyqt-preview --version    # Show version and exit
pyqt-preview --help       # Show help message
```

## Window Focus Behavior Across Operating Systems

PyQt Preview attempts to minimize disruption to your workflow when reloading the UI. On some operating systems, PyQt/Qt applications may steal window focus from your editor or terminal when reloaded or launched. This behavior and available workarounds vary by platform:

| OS      | Focus Stealing Issue | Workarounds/Limitations                | Best Practice                |
|---------|---------------------|----------------------------------------|------------------------------|
| macOS   | Yes                 | AppleScript, but not 100% reliable     | Provide opt-in flag, document|
| Windows | Yes                 | SetForegroundWindow, AutoHotkey, limited| Avoid, document limitation   |
| Linux   | Yes                 | wmctrl/xdotool, fragile                | Avoid, respect WM policy     |

- **macOS:** Use the `--keep-window-focus` flag (or `keep_window_focus = true` in config) to attempt to restore focus to your previously active app after UI reloads. This uses AppleScript and may not work with all editors or in all scenarios.
- **Windows & Linux:** Focus stealing is restricted by OS policies. There is no reliable, cross-platform way to restore focus to your previous app. Attempts to do so may be blocked or behave inconsistently. PyQt Preview does not support focus restoration on these platforms.

**Flag distinction:**
- `--preserve-state` preserves the window position and size (geometry) across reloads. It does not affect which application is focused.
- `--keep-window-focus` prevents the PyQt window from stealing focus on macOS, restoring focus to your editor or previously active app after reload. It does not affect window geometry.
- These flags are independent and can be used together for best workflow experience.

## Troubleshooting & FAQ

- **UI compiler not found:** Install the appropriate Qt tools (`pyuic6`, `pyuic5`, `pyside6-uic`, `pyside2-uic`).
- **Changes not detected:** Check your file patterns and ensure your editor saves files.
- **Too many reloads:** Increase `reload_delay` and add more ignore patterns.
- **Import errors after reload:** Check your `PYTHONPATH`, use absolute imports, and verify your project structure.
- **Verbose output:** Use `--verbose` for detailed logs.

## Roadmap

### Completed Features
- [x] Live reload for Python files
- [x] Automatic UI file compilation
- [x] Multi-framework support (PyQt5/6, PySide2/6)
- [x] Window state preservation
- [x] TOML configuration system
- [x] CLI with subcommands

### Planned Features
- [ ] Hot widget replacement (soft reload without full restart)
- [ ] Qt Designer integration improvements
- [ ] VS Code extension
- [ ] Plugin system for custom reload behaviors
- [ ] Remote preview capabilities
- [ ] Template system for common PyQt patterns
- [ ] AI/MCP integration (experimental/future)

## Documentation

- **[Quick Start Guide](TUTORIAL.md)**
- **[Complete Tutorial](docs/tutorials/getting-started.md)**
- **[Examples](examples/README.md)**
- **[Architecture Guide](docs/guides/architecture-guide.md)**

## Development & Contributing

### Setup

```bash
# Clone and enter directory
git clone https://github.com/your-username/pyqt-preview.git
cd pyqt-preview

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=pyqt_preview --cov-report=html
```

### Code Quality

```bash
black src/ tests/
isort src/ tests/
mypy src/
flake8 src/ tests/
```

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, code style, and PR process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by modern web development live reload tools
- Built with the excellent [watchdog](https://github.com/gorakhargosh/watchdog) library
- Thanks to the PyQt and Qt communities

---

**Made with love for the PyQt community**
