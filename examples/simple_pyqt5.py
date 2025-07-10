"""
PyQt5 version of the simple example application.

This demonstrates compatibility with PyQt5 for users who prefer or need
to use the older version.
"""

import os
import sys
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Main application window for PyQt5."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Preview Demo")
        self.setGeometry(100, 100, 600, 400)

        # Restore geometry if provided
        if "PYQT_PREVIEW_GEOMETRY" in os.environ:
            try:
                geom = os.environ["PYQT_PREVIEW_GEOMETRY"].split(",")
                x, y, width, height = map(int, geom)
                self.setGeometry(x, y, width, height)
            except (ValueError, IndexError):
                pass

        self.setup_ui()
        self.counter = 0

        # Timer for status updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)

    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("PyQt5 Live Preview Demo")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)

        # Info
        info = QLabel("This is the PyQt5 version. Edit and save to see changes!")
        layout.addWidget(info)

        # Simple interaction
        self.button = QPushButton("Click me!")
        self.button.clicked.connect(self.on_button_click)
        layout.addWidget(self.button)

        self.result_label = QLabel("No clicks yet")
        layout.addWidget(self.result_label)

        # Status
        self.status_label = QLabel("Running...")
        layout.addWidget(self.status_label)

    def on_button_click(self):
        """Handle button click."""
        self.counter += 1
        self.result_label.setText(f"Button clicked {self.counter} times!")

    def update_status(self):
        """Update status."""
        self.status_label.setText(f"PyQt5 app running - {time.strftime('%H:%M:%S')}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
