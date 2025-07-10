"""
Example app that uses a .ui file compiled to Python.

This demonstrates how PyQt Preview automatically compiles .ui files
when they change, enabling seamless integration with Qt Designer.
"""

import os
import sys

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow

# Import the compiled UI file (will be generated automatically)
try:
    from demo import Ui_MainWindow  # This will be generated from demo.ui
except ImportError:
    print("WARNING: demo.py not found. Please run 'pyuic6 demo.ui -o demo.py' first")
    print("   Or use pyqt-preview which will compile it automatically!")
    sys.exit(1)


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main window that uses the .ui file."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Restore geometry if provided by PyQt Preview
        if "PYQT_PREVIEW_GEOMETRY" in os.environ:
            try:
                geom = os.environ["PYQT_PREVIEW_GEOMETRY"].split(",")
                x, y, width, height = map(int, geom)
                self.setGeometry(x, y, width, height)
            except (ValueError, IndexError):
                pass

        # Connect signals
        self.greetButton.clicked.connect(self.on_greet_clicked)
        self.clearButton.clicked.connect(self.on_clear_clicked)
        self.nameInput.returnPressed.connect(self.on_greet_clicked)

    @pyqtSlot()
    def on_greet_clicked(self):
        """Handle greet button click."""
        name = self.nameInput.text().strip()
        greeting = f"Hello, {name}! 👋" if name else "Hello, World! 🌍"

        self.outputText.append(greeting)
        self.nameInput.clear()

    @pyqtSlot()
    def on_clear_clicked(self):
        """Handle clear button click."""
        self.outputText.clear()
        self.outputText.append("Output cleared. Ready for new greetings!")


def main():
    """Main function."""
    app = QApplication(sys.argv)
    app.setApplicationName("UI File Demo")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
