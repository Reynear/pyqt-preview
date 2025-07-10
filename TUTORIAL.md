# PyQt Preview - Quick Start Guide

Get up and running with PyQt Preview!

## Prerequisites

```bash
pip install pyqt6  # or pyqt5
pip install pyqt-preview
```

## Quick Start

### 1. Create a Simple App

Create `hello.py`:

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget

class HelloApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello PyQt Preview")  # Try changing this!
        self.setGeometry(100, 100, 400, 200)
        
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        label = QLabel("Hello, World!")
        label.setStyleSheet("font-size: 24px; color: blue;")  # Try changing the color!
        
        button = QPushButton("Click Me!")
        button.setStyleSheet("background-color: green; color: white; padding: 10px;")
        button.clicked.connect(lambda: label.setText("Button Clicked!"))
        
        layout.addWidget(label)
        layout.addWidget(button)

def main():
    app = QApplication(sys.argv)
    window = HelloApp()
    window.show()
    return app.exec()

if __name__ == "__main__":
    main()
```

### 2. Start PyQt Preview 

```bash
pyqt-preview hello.py
```

### 3. Try Live Editing 

With the app running, edit `hello.py`:

- Change the window title
- Change colors in stylesheets
- Modify button text
- Add new widgets

Save the file and watch it reload instantly!

## Qt Designer Quick Start

### 1. Create UI File

Save as `simple.ui`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="windowTitle">
   <string>Designer App</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout">
    <item>
     <widget class="QPushButton" name="myButton">
      <property name="text">
       <string>Designer Button</string>
      </property>
     </widget>
    </item>
   </layout>
  </widget>
 </widget>
</ui>
```

### 2. Create Python File

Save as `ui_app.py`:
```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from simple import Ui_MainWindow  # Auto-compiled by PyQt Preview

class UIApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.myButton.clicked.connect(lambda: print("UI Button clicked!"))

def main():
    app = QApplication(sys.argv)
    window = UIApp()
    window.show()
    return app.exec()

if __name__ == "__main__":
    main()
```

### 3. Run with Auto-Compilation

```bash
pyqt-preview ui_app.py
```

Edit the `.ui` file and watch both the UI compilation and app reload happen automatically!

## Configuration (Optional)

Create `.pyqt-preview.toml` for custom settings:

```toml
[tool.pyqt-preview]
framework = "pyqt6"
reload_delay = 0.3
preserve_window_state = true
verbose = true

watch_patterns = ["*.py", "*.ui"]
ignore_patterns = ["__pycache__", "*.pyc"]
```

## Common Commands

```bash
# Basic usage
pyqt-preview app.py

# With verbose output
pyqt-preview app.py --verbose

# Specify framework
pyqt-preview app.py --framework pyqt5

# Check configuration
pyqt-preview check
```

## Next Steps

For detailed tutorials, advanced configuration, and troubleshooting:

👉 **[Complete Tutorial Guide](docs/tutorials/getting-started.md)**

## Need Help?

- **Check verbose output**: `pyqt-preview app.py --verbose`
- **Verify setup**: `pyqt-preview check`  
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory

