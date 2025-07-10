# PyQt Preview - Live Preview Tool for PyQt GUI Development

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/your-username/pyqt-preview)

A development tool for PyQt5/PyQt6 GUI applications that provides live reloading when editing `.py` or `.ui` files—speeding up the development process.

## Features

- **Live Reload**: Instantly reloads your PyQt application when files change
- **UI Compilation**: Automatically compiles .ui files to Python code
- **Multiple Frameworks**: Supports PyQt5, PyQt6, PySide2, and PySide6
- **Smart Watching**: Configurable file patterns and ignore rules
- **Zero Configuration**: Works out of the box with sensible defaults
- **Preserve State**: Maintains window position and size across reloads
- **Flexible Config**: TOML-based configuration with CLI overrides

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

## Requirements

- Python 3.8+
- PyQt5/PyQt6 or PySide2/PySide6
- watchdog

## How It Works

```
┌────────────────────────────┐
│ Developer edits UI files   │
└────────────┬───────────────┘
             ▼
   ┌────────────────────┐
   │ File Watcher       │
   │ (watchdog)         │
   └────────┬───────────┘
            ▼
 ┌────────────────────────┐
 │ Build & Launch Handler │
 │ - Recompile .ui files  │
 │ - Restart GUI App      │
 └────────────┬───────────┘
              ▼
    ┌────────────────────┐
    │ PyQt Preview Window │
    └────────────────────┘
```

## Configuration

Create a `.pyqt-preview.toml` file in your project root:

```toml
[tool.pyqt-preview]
framework = "pyqt6"  # pyqt5, pyqt6, pyside2, pyside6
watch_patterns = ["*.py", "*.ui"]
ignore_patterns = ["__pycache__", "*.pyc"]
ui_compiler = "auto"  # auto, pyuic5, pyuic6, pyside2-uic, pyside6-uic
preserve_window_state = true
reload_delay = 0.5  # seconds
```

## Examples

### Example 1: Simple PyQt Application

```python
# app.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setGeometry(100, 100, 400, 300)
        
        label = QLabel("Hello, PyQt!", self)
        self.setCentralWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

Run with preview:
```bash
pyqt-preview run app.py
```

### Example 2: Using UI Files

```bash
# Create your UI in Qt Designer, save as main.ui
pyqt-preview run app.py --watch . --ui-dir ui/
```

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
  --config PATH         Path to configuration file
  --verbose            Enable verbose logging
  --help               Show this message and exit
```

**Examples:**
```bash
# Basic usage
pyqt-preview run app.py

# Watch specific directory with custom framework
pyqt-preview run app.py --watch src/ --framework pyqt6

# Custom reload delay and verbose output
pyqt-preview run app.py --reload-delay 1.0 --verbose

# Use custom configuration file
pyqt-preview run app.py --config my-config.toml
```

### `init` Command

Initialize a new PyQt Preview configuration file.

```bash
pyqt-preview init [OPTIONS]

Options:
  --dir PATH           Directory to initialize [default: current directory]
  --framework TEXT     GUI framework (pyqt5|pyqt6|pyside2|pyside6) [default: pyqt6]
  --force             Overwrite existing configuration
  --help              Show this message and exit
```

**Examples:**
```bash
# Create config in current directory
pyqt-preview init

# Create config for PyQt5 project
pyqt-preview init --framework pyqt5

# Initialize in specific directory
pyqt-preview init --dir my-project/

# Force overwrite existing config
pyqt-preview init --force
```

### `check` Command

Check the current configuration and system requirements.

```bash
pyqt-preview check [OPTIONS]

Options:
  --config PATH        Path to configuration file
  --help              Show this message and exit
```

**Examples:**
```bash
# Check system with default config
pyqt-preview check

# Check with custom config file
pyqt-preview check --config my-config.toml
```

### Global Options

```bash
pyqt-preview --version    # Show version and exit
pyqt-preview --help       # Show help message
```

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
- [ ] Qt Designer integration
- [ ] VS Code extension
- [ ] Plugin system for custom reload behaviors
- [ ] Remote preview capabilities
- [ ] Template system for common PyQt patterns

## Documentation

### Getting Started

- **[5-Minute Quick Start](TUTORIAL.md)** - Get running fast with essential examples
- **[Complete Tutorial](docs/tutorials/getting-started.md)** - Comprehensive hands-on guide
- **[Examples](examples/README.md)** - Working example applications

### Advanced Documentation

- **[Architecture Guide](docs/guides/architecture-guide.md)** - Detailed technical overview



## Installation

### From PyPI (Recommended)

```bash
pip install pyqt-preview
```

### From Source

For the latest development version or to contribute:

```bash
# Clone the repository
git clone https://github.com/your-username/pyqt-preview.git
cd pyqt-preview

# Quick setup with script (Unix/Linux/macOS)
./scripts/setup-dev.sh

# Or Windows
scripts/setup-dev.bat

# Or manual setup
pip install -e ".[dev]"
```

## Development

### Prerequisites

- Python 3.8+
- Git
- PyQt5/PyQt6 or PySide2/PySide6

### Setup Development Environment

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
# Run all tests
pytest

# Run with coverage
pytest --cov=pyqt_preview

# Run specific test file
pytest tests/test_config.py
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Building Distribution

```bash
# Build wheel and source distribution
python -m build

# Install from local build
pip install dist/pyqt_preview-*.whl
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by modern web development live reload tools
- Built with the excellent [watchdog](https://github.com/gorakhargosh/watchdog) library
- Thanks to the PyQt and Qt communities
  
---

**Made with love for the PyQt community**
