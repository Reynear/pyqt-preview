# PyQt Preview - Hands-On Tutorial

This tutorial will walk you through using PyQt Preview step-by-step with real examples you can try yourself.

## Tutorial 1: Your First Live Reload App

### Step 1: Create a Simple PyQt App

Create a new file called `tutorial_app.py`:

```python
# tutorial_app.py
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QLineEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class TutorialApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Preview Tutorial")  # Try changing this!
        self.setGeometry(100, 100, 500, 400)
        
        # Enable window state preservation
        self.restore_geometry()
        
        # Setup UI
        self.init_ui()
        
        # Track clicks
        self.click_count = 0
    
    def restore_geometry(self):
        """Restore window position from PyQt Preview."""
        if 'PYQT_PREVIEW_GEOMETRY' in os.environ:
            try:
                geom = os.environ['PYQT_PREVIEW_GEOMETRY'].split(',')
                x, y, width, height = map(int, geom)
                self.setGeometry(x, y, width, height)
            except (ValueError, IndexError):
                pass  # Use default geometry if parsing fails
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Welcome to PyQt Preview!")  # Try changing this text!
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2E86AB; margin: 20px;")  # Try changing this color!
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Edit this file and save to see live updates!")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(subtitle)
        
        # Input section
        input_layout = QHBoxLayout()
        input_label = QLabel("Your name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name here...")
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.name_input)
        layout.addLayout(input_layout)
        
        # Button
        self.greet_button = QPushButton("Say Hello!")  # Try changing this text!
        self.greet_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Try changing this color! */
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        self.greet_button.clicked.connect(self.on_greet_click)
        layout.addWidget(self.greet_button)
        
        # Result display
        self.result_label = QLabel("Click the button to get started!")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            font-size: 14px;
            margin: 10px;
        """)
        layout.addWidget(self.result_label)
        
        # Statistics
        self.stats_label = QLabel("Clicks: 0 | Reloads: Check console")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.stats_label)
    
    def on_greet_click(self):
        """Handle the greet button click."""
        name = self.name_input.text().strip()
        self.click_count += 1
        
        if name:
            message = f"Hello, {name}! 👋"
        else:
            message = "Hello, Anonymous! 😊"
        
        # Try changing these messages!
        self.result_label.setText(message)
        self.stats_label.setText(f"Clicks: {self.click_count} | Keep editing and saving!")
        
        # Clear input
        self.name_input.clear()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PyQt Preview Tutorial")
    
    window = TutorialApp()
    window.show()
    
    print("Tutorial app started! Try editing tutorial_app.py and saving.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### Step 2: Run with PyQt Preview

```bash
# Start PyQt Preview
pyqt-preview run tutorial_app.py --verbose
```

You should see:
```
PyQt Preview started!
Watching: /your/project/directory
Script: tutorial_app.py
Framework: pyqt6
Reload delay: 0.5s
State preservation: enabled
Press Ctrl+C to stop
```

### Step 3: Try Live Editing!

Now, with the app running, try these edits:

1. **Change the window title** (line 17):
   ```python
   self.setWindowTitle("My Amazing Live App!")  # Save and watch it change!
   ```

2. **Change the button color** (line 62):
   ```python
   background-color: #FF6B6B;  /* Try red instead of green! */
   ```

3. **Change the button text** (line 55):
   ```python
   self.greet_button = QPushButton("Click Me!")  # Try different text!
   ```

4. **Modify the greeting message** (line 92):
   ```python
   message = f"Greetings, {name}! 🎊"  # Try different messages!
   ```

Each time you save, you'll see:
```
File changed: tutorial_app.py
Restarting application...
Reload #1 completed
```

---

## Tutorial 2: Working with Qt Designer

### Step 1: Create a UI File

Create `calculator.ui` using Qt Designer, or save this content to a file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>CalculatorWindow</class>
 <widget class="QMainWindow" name="CalculatorWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>300</width>
    <height>400</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Live Calculator</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout" name="verticalLayout">
    <item>
     <widget class="QLineEdit" name="display">
      <property name="readOnly">
       <bool>true</bool>
      </property>
      <property name="alignment">
       <set>Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter</set>
      </property>
      <property name="styleSheet">
       <string>font-size: 24px; padding: 10px; background-color: #f0f0f0;</string>
      </property>
     </widget>
    </item>
    <item>
     <layout class="QGridLayout" name="buttonGrid">
      <item row="0" column="0">
       <widget class="QPushButton" name="btn7">
        <property name="text">
         <string>7</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="0" column="1">
       <widget class="QPushButton" name="btn8">
        <property name="text">
         <string>8</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="0" column="2">
       <widget class="QPushButton" name="btn9">
        <property name="text">
         <string>9</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="0" column="3">
       <widget class="QPushButton" name="btnDivide">
        <property name="text">
         <string>/</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
        <property name="styleSheet">
         <string>background-color: #FF9500; color: white;</string>
        </property>
       </widget>
      </item>
      <item row="1" column="0">
       <widget class="QPushButton" name="btn4">
        <property name="text">
         <string>4</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="1" column="1">
       <widget class="QPushButton" name="btn5">
        <property name="text">
         <string>5</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="1" column="2">
       <widget class="QPushButton" name="btn6">
        <property name="text">
         <string>6</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="1" column="3">
       <widget class="QPushButton" name="btnMultiply">
        <property name="text">
         <string>*</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
        <property name="styleSheet">
         <string>background-color: #FF9500; color: white;</string>
        </property>
       </widget>
      </item>
      <item row="2" column="0">
       <widget class="QPushButton" name="btn1">
        <property name="text">
         <string>1</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="2" column="1">
       <widget class="QPushButton" name="btn2">
        <property name="text">
         <string>2</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="2" column="2">
       <widget class="QPushButton" name="btn3">
        <property name="text">
         <string>3</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="2" column="3">
       <widget class="QPushButton" name="btnSubtract">
        <property name="text">
         <string>-</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
        <property name="styleSheet">
         <string>background-color: #FF9500; color: white;</string>
        </property>
       </widget>
      </item>
      <item row="3" column="0" colspan="2">
       <widget class="QPushButton" name="btn0">
        <property name="text">
         <string>0</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>120</width>
          <height>60</height>
         </size>
        </property>
       </widget>
      </item>
      <item row="3" column="2">
       <widget class="QPushButton" name="btnClear">
        <property name="text">
         <string>C</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
        <property name="styleSheet">
         <string>background-color: #FF3B30; color: white;</string>
        </property>
       </widget>
      </item>
      <item row="3" column="3">
       <widget class="QPushButton" name="btnAdd">
        <property name="text">
         <string>+</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>60</width>
          <height>60</height>
         </size>
        </property>
        <property name="styleSheet">
         <string>background-color: #FF9500; color: white;</string>
        </property>
       </widget>
      </item>
      <item row="4" column="0" colspan="4">
       <widget class="QPushButton" name="btnEquals">
        <property name="text">
         <string>=</string>
        </property>
        <property name="minimumSize">
         <size>
          <width>240</width>
          <height>60</height>
         </size>
        </property>
        <property name="styleSheet">
         <string>background-color: #007AFF; color: white; font-weight: bold;</string>
        </property>
       </widget>
      </item>
     </layout>
    </item>
   </layout>
  </widget>
 </widget>
</ui>
```

### Step 2: Create the Python Application

Create `calculator_app.py`:

```python
# calculator_app.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import pyqtSlot

# Import the compiled UI file (will be auto-generated by PyQt Preview)
try:
    from calculator import Ui_CalculatorWindow
except ImportError:
    print("ERROR: calculator.py not found. PyQt Preview will compile it automatically!")
    print("Just save this file and the UI will be generated.")
    sys.exit(1)

class CalculatorApp(QMainWindow, Ui_CalculatorWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Restore geometry from PyQt Preview
        self.restore_geometry()
        
        # Calculator state
        self.current_value = "0"
        self.operator = None
        self.waiting_for_operand = False
        self.stored_value = 0
        
        # Connect all buttons
        self.connect_buttons()
        
        # Initial display update
        self.update_display()
    
    def restore_geometry(self):
        """Restore window position from PyQt Preview."""
        if 'PYQT_PREVIEW_GEOMETRY' in os.environ:
            try:
                geom = os.environ['PYQT_PREVIEW_GEOMETRY'].split(',')
                x, y, width, height = map(int, geom)
                self.setGeometry(x, y, width, height)
            except (ValueError, IndexError):
                pass
    
    def connect_buttons(self):
        """Connect all calculator buttons to their handlers."""
        # Number buttons
        for i in range(10):
            button = getattr(self, f'btn{i}')
            button.clicked.connect(lambda checked, num=i: self.number_clicked(num))
        
        # Operator buttons
        self.btnAdd.clicked.connect(lambda: self.operator_clicked('+'))
        self.btnSubtract.clicked.connect(lambda: self.operator_clicked('-'))
        self.btnMultiply.clicked.connect(lambda: self.operator_clicked('*'))
        self.btnDivide.clicked.connect(lambda: self.operator_clicked('/'))
        
        # Special buttons
        self.btnEquals.clicked.connect(self.equals_clicked)
        self.btnClear.clicked.connect(self.clear_clicked)
    
    def update_display(self):
        """Update the calculator display."""
        self.display.setText(self.current_value)
    
    def number_clicked(self, number):
        """Handle number button clicks."""
        if self.waiting_for_operand:
            self.current_value = str(number)
            self.waiting_for_operand = False
        else:
            if self.current_value == "0":
                self.current_value = str(number)
            else:
                self.current_value += str(number)
        
        self.update_display()
    
    def operator_clicked(self, op):
        """Handle operator button clicks."""
        if self.operator and not self.waiting_for_operand:
            self.equals_clicked()
        
        self.stored_value = float(self.current_value)
        self.operator = op
        self.waiting_for_operand = True
    
    def equals_clicked(self):
        """Handle equals button click."""
        if self.operator and not self.waiting_for_operand:
            try:
                current = float(self.current_value)
                
                if self.operator == '+':
                    result = self.stored_value + current
                elif self.operator == '-':
                    result = self.stored_value - current
                elif self.operator == '*':
                    result = self.stored_value * current
                elif self.operator == '/':
                    if current == 0:
                        self.current_value = "Error"
                        self.update_display()
                        return
                    result = self.stored_value / current
                
                # Format result
                if result == int(result):
                    self.current_value = str(int(result))
                else:
                    self.current_value = f"{result:.8g}"
                
                self.operator = None
                self.waiting_for_operand = True
                self.update_display()
                
            except (ValueError, ZeroDivisionError):
                self.current_value = "Error"
                self.update_display()
    
    def clear_clicked(self):
        """Handle clear button click."""
        self.current_value = "0"
        self.operator = None
        self.waiting_for_operand = False
        self.stored_value = 0
        self.update_display()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Live Calculator")
    
    calculator = CalculatorApp()
    calculator.show()
    
    print("Calculator started! Try editing calculator.ui in Qt Designer!")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### Step 3: Run with UI File Compilation

```bash
# Start PyQt Preview with UI compilation
pyqt-preview run calculator_app.py --ui-dir . --verbose
```

You'll see:
```
[INFO] Compiling calculator.ui -> calculator.py
[OK] Compiled calculator.ui
[INFO] Starting application: calculator_app.py
```

### Step 4: Edit the UI File

Now try editing the `calculator.ui` file:

1. **Change button colors** in the XML:
   ```xml
   <property name="styleSheet">
    <string>background-color: #34C759; color: white;</string>  <!-- Green instead of orange -->
   </property>
   ```

2. **Change the window title**:
   ```xml
   <property name="windowTitle">
    <string>My Amazing Calculator</string>
   </property>
   ```

3. **Modify button sizes**:
   ```xml
   <property name="minimumSize">
    <size>
     <width>80</width>  <!-- Wider buttons -->
     <height>80</height>  <!-- Taller buttons -->
    </size>
   </property>
   ```

Each time you save the UI file, PyQt Preview will:
1. Detect the change
2. Recompile `calculator.ui` to `calculator.py`
3. Restart your application
4. Show the updated interface!

---

## 🎯 Tutorial 3: Advanced Configuration

### Step 1: Create a Project Structure

```
my_project/
├── src/
│   ├── main.py
│   ├── widgets/
│   │   └── custom_widget.py
│   └── generated/  (auto-created)
├── ui/
│   ├── main.ui
│   └── dialogs/
│       └── settings.ui
├── resources/
│   └── style.qss
└── .pyqt-preview.toml
```

### Step 2: Configure PyQt Preview

Create `.pyqt-preview.toml`:

```toml
[tool.pyqt-preview]
# Framework selection
framework = "pyqt6"
ui_compiler = "auto"

# File watching
watch_patterns = ["*.py", "*.ui", "*.qss"]
ignore_patterns = [
    "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    ".git", ".venv", "venv", "node_modules",
    "src/generated/*",  # Ignore auto-generated files
    "test_*.py", "*_test.py"  # Ignore test files
]

# Directories
ui_dir = "ui/"
output_dir = "src/generated/"

# Reload behavior
reload_delay = 0.3  # Faster reload for better experience
preserve_window_state = true

# Logging
verbose = true
```

### Step 3: Create the Main Application

Create `src/main.py`:

```python
# src/main.py
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

# Add generated files to path
sys.path.insert(0, str(Path(__file__).parent / "generated"))

try:
    from main import Ui_MainWindow
    UI_AVAILABLE = True
except ImportError:
    print("WARNING: UI file not compiled yet. Will use code-based UI.")
    UI_AVAILABLE = False

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        if UI_AVAILABLE:
            # Use compiled UI
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.setup_ui_connections()
        else:
            # Fallback to code-based UI
            self.setup_code_ui()
        
        self.restore_geometry()
    
    def restore_geometry(self):
        """Restore window geometry from PyQt Preview."""
        if 'PYQT_PREVIEW_GEOMETRY' in os.environ:
            try:
                geom = os.environ['PYQT_PREVIEW_GEOMETRY'].split(',')
                x, y, width, height = map(int, geom)
                self.setGeometry(x, y, width, height)
            except (ValueError, IndexError):
                pass
    
    def setup_ui_connections(self):
        """Connect UI elements when using compiled UI."""
        # Example: Connect buttons defined in UI file
        if hasattr(self.ui, 'actionButton'):
            self.ui.actionButton.clicked.connect(self.on_action)
    
    def setup_code_ui(self):
        """Setup UI using code when UI file is not available."""
        self.setWindowTitle("PyQt Preview Demo (Code UI)")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        button = QPushButton("UI file will replace this when compiled!")
        button.clicked.connect(self.on_action)
        layout.addWidget(button)
    
    def on_action(self):
        """Handle button clicks."""
        print("Action triggered! Try editing the UI file or this Python code.")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced PyQt Preview Demo")
    
    # Load stylesheet if available
    style_path = Path(__file__).parent.parent / "resources" / "style.qss"
    if style_path.exists():
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())
    
    window = MainApp()
    window.show()
    
    print("Advanced demo started!")
    print("   • Edit src/main.py for code changes")
    print("   • Edit ui/main.ui for UI changes") 
    print("   • Edit resources/style.qss for styling")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### Step 4: Create Supporting Files

Create `ui/main.ui`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="windowTitle">
   <string>Advanced PyQt Preview Demo</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout">
    <item>
     <widget class="QLabel" name="titleLabel">
      <property name="text">
       <string>This UI was loaded from a .ui file!</string>
      </property>
      <property name="alignment">
       <set>Qt::AlignCenter</set>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QPushButton" name="actionButton">
      <property name="text">
       <string>UI File Button</string>
      </property>
     </widget>
    </item>
   </layout>
  </widget>
 </widget>
</ui>
```

Create `resources/style.qss`:
```css
/* Global styling */
QMainWindow {
    background-color: #f5f5f5;
}

QPushButton {
    background-color: #007AFF;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #0056CC;
}

QPushButton:pressed {
    background-color: #004499;
}

QLabel {
    color: #333;
    font-size: 16px;
    padding: 10px;
}
```

### Step 5: Run the Advanced Setup

```bash
# From the project root
pyqt-preview run src/main.py

# Or with explicit configuration
pyqt-preview run src/main.py --config .pyqt-preview.toml
```

Now you can edit:
- **Python code** in `src/`
- **UI files** in `ui/` (auto-compiled to `src/generated/`)
- **Stylesheets** in `resources/`

All changes will trigger automatic reloads!

---

## Tutorial 4: Debugging and Troubleshooting

### Common Issues and Solutions

#### Issue 1: "UI compiler not found"

**Problem**: PyQt Preview can't find `pyuic6` or similar.

**Solution**:
```bash
# For PyQt6
pip install PyQt6-tools

# For PyQt5  
pip install PyQt5-tools

# Verify installation
pyqt-preview check
```

#### Issue 2: "Changes not detected"

**Problem**: File changes don't trigger reloads.

**Debug steps**:
```bash
# Run with verbose output
pyqt-preview run app.py --verbose

# Check what files are being watched
pyqt-preview run app.py --verbose 2>&1 | grep "Watching"

# Verify your file patterns
cat .pyqt-preview.toml
```

**Common solutions**:
- Make sure your editor actually saves files
- Check file patterns in configuration
- Add problematic directories to `ignore_patterns`

#### Issue 3: "Too many reloads"

**Problem**: App reloads constantly.

**Solution**:
```toml
# Increase reload delay
[tool.pyqt-preview]
reload_delay = 2.0  # Wait 2 seconds between reloads

# Ignore more file types
ignore_patterns = [
    "__pycache__", "*.pyc", "*.pyo",
    ".git", "venv", ".venv",
    "*.log", "*.tmp", ".DS_Store"
]
```

#### Issue 4: "Import errors after reload"

**Problem**: Python imports fail after restart.

**Solution**:
- Check your `PYTHONPATH`
- Ensure all dependencies are installed
- Use absolute imports where possible
- Verify your project structure

---

## Conclusion

You now know how to:

1. **Set up PyQt Preview** for any project
2. **Use live reload** for rapid development
3. **Integrate Qt Designer** with automatic UI compilation
4. **Configure advanced workflows** with TOML files
5. **Debug common issues** and optimize performance

**Next Steps:**
- Try PyQt Preview with your own projects
- Experiment with different configurations
- Integrate with your preferred IDE/editor
- Share your experience with the community!

**Happy coding with PyQt Preview!**
