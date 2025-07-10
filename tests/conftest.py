"""
Test configuration for PyQt Preview tests.
"""

import sys
from pathlib import Path

import pytest

# Add the src directory to Python path for testing
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_py_file(temp_dir):
    """Create a sample Python file for testing."""
    py_file = temp_dir / "test.py"
    py_file.write_text(
        """
import sys
from PyQt6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("Hello, World!")
label.show()
app.exec()
"""
    )
    return py_file


@pytest.fixture
def sample_ui_file(temp_dir):
    """Create a sample UI file for testing."""
    ui_file = temp_dir / "test.ui"
    ui_file.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>300</width>
    <height>200</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Test Window</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QLabel" name="label">
    <property name="geometry">
     <rect>
      <x>50</x>
      <y>50</y>
      <width>200</width>
      <height>100</height>
     </rect>
    </property>
    <property name="text">
     <string>Hello from UI file</string>
    </property>
   </widget>
  </widget>
 </widget>
</ui>"""
    )
    return ui_file
