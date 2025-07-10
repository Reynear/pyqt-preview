"""
Simple PyQt6 example application for testing PyQt Preview.

This is a basic application that demonstrates live reloading capabilities.
Try editing the window title, button text, or layout and save to see changes!
"""

import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Preview Demo App")  # Try changing this!
        self.setGeometry(100, 100, 600, 400)

        # Restore geometry if provided by PyQt Preview
        if "PYQT_PREVIEW_GEOMETRY" in os.environ:
            try:
                geom = os.environ["PYQT_PREVIEW_GEOMETRY"].split(",")
                x, y, width, height = map(int, geom)
                self.setGeometry(x, y, width, height)
            except (ValueError, IndexError):
                pass  # Use default geometry if parsing fails

        # Initialize the UI
        self.init_ui()

        # Track click count
        self.click_count = 0

    def init_ui(self):
        """Initialize the user interface."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create title label
        title = QLabel("Welcome to PyQt Preview!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px 0;
            }
        """)

        # Create subtitle
        subtitle = QLabel("This is a live-reload demonstration")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)

        # Create input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type something here...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 16px;
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
            QLineEdit:focus {
                border-color: #2980b9;
                background-color: white;
            }
        """)

        # Create button
        self.button = QPushButton("Click Me!")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        # Create output label
        self.output_label = QLabel("Enter text above and click the button!")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #34495e;
                margin: 20px 0;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
            }
        """)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.input_field)
        layout.addWidget(self.button)
        layout.addWidget(self.output_label)

        # Connect button click
        self.button.clicked.connect(self.on_button_click)

        # Connect enter key in input field
        self.input_field.returnPressed.connect(self.on_button_click)

    def on_button_click(self):
        """Handle button click."""
        text = self.input_field.text()
        self.click_count += 1

        if text:
            message = f"Hello, {text}!"
            self.output_label.setText(f"{message} (Click #{self.click_count})")
        else:
            self.output_label.setText(f"Please enter some text! (Click #{self.click_count})")

        # Clear input field
        self.input_field.clear()

        # Focus back to input field
        self.input_field.setFocus()

    def on_clear_clicked(self):
        """Clear the output area."""
        self.output_label.setText("Output cleared!")
        self.input_field.clear()
        self.input_field.setFocus()

    def update_status(self, message):
        """Update the status message."""
        print(f"Status: {message}")


def main():
    """Main function."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("PyQt Preview Demo")
    app.setApplicationVersion("1.0.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
