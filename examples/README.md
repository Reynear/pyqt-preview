# PyQt Preview Examples

This directory contains example applications to demonstrate PyQt Preview capabilities.

## Getting Started

1. Install PyQt Preview (if not already installed):
   ```bash
   pip install pyqt-preview
   ```
2. Run any example:
   ```bash
   cd examples
   pyqt-preview run simple_app.py
   ```
3. Edit the Python file and save to see live updates!

## Example Applications

### 1. `simple_app.py` - Basic PyQt6 Application
- Window geometry preservation
- Interactive widgets
- Styling with CSS
- Timer-based updates
- Signal/slot connections

**Run with:**
```bash
pyqt-preview run simple_app.py
```

### 2. `simple_pyqt5.py` - PyQt5 Compatibility
- Basic widget interactions
- Timer updates
- Cross-version compatibility

**Run with:**
```bash
pyqt-preview run simple_pyqt5.py --framework pyqt5
```

### 3. `ui_app.py` + `demo.ui` - Qt Designer Integration
- Uses Qt Designer generated .ui file
- Automatic compilation to Python
- Designer integration workflow

**Run with:**
```bash
pyqt-preview run ui_app.py --ui-dir .
```

## Tips for Testing

- **Edit window titles** - Change the `setWindowTitle()` calls
- **Modify button text** - Update button labels and see instant changes
- **Adjust colors** - Change the stylesheet colors
- **Add new widgets** - Try adding new UI elements
- **Edit .ui files** - Open `demo.ui` in Qt Designer, make changes, and save

## Configuration

Create a `.pyqt-preview.toml` file for project-specific settings:

```toml
[tool.pyqt-preview]
framework = "pyqt6"
watch_patterns = ["*.py", "*.ui"]
reload_delay = 0.5
preserve_window_state = true
```

## Troubleshooting

If you encounter issues:
1. **Check your PyQt installation:**
   ```bash
   pyqt-preview check
   ```
2. **Enable verbose output:**
   ```bash
   pyqt-preview run simple_app.py --verbose
   ```
3. **Check for UI compiler:**
   - PyQt6: Ensure `pyuic6` is available
   - PyQt5: Ensure `pyuic5` is available
   - PySide: Ensure `pyside6-uic` or `pyside2-uic` is available

## Advanced Usage

- Use custom config files for advanced workflows
- Try different frameworks and UI setups
- Experiment with reload delay and ignore patterns

For more examples and documentation, see the main project README and docs directory.
