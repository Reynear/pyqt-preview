#!/bin/bash
# Development setup script for PyQt Preview

set -e

echo "Setting up PyQt Preview development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d ' ' -f2 | cut -d '.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.8+ required (found Python $python_version)"
    exit 1
fi

echo "Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install development dependencies
echo "Installing PyQt Preview in development mode..."
pip install -e ".[dev]"

# Verify installation
echo "Verifying installation..."
if pyqt-preview --version > /dev/null 2>&1; then
    echo "PyQt Preview installed successfully!"
    pyqt-preview --version
else
    echo "ERROR: Installation verification failed"
    exit 1
fi

# Check for GUI frameworks
echo "Checking GUI frameworks..."
gui_frameworks=()

if python -c "import PyQt6" 2>/dev/null; then
    gui_frameworks+=("PyQt6")
fi

if python -c "import PyQt5" 2>/dev/null; then
    gui_frameworks+=("PyQt5")
fi

if python -c "import PySide6" 2>/dev/null; then
    gui_frameworks+=("PySide6")
fi

if python -c "import PySide2" 2>/dev/null; then
    gui_frameworks+=("PySide2")
fi

if [ ${#gui_frameworks[@]} -eq 0 ]; then
    echo "WARNING: No GUI frameworks detected. Installing PyQt6..."
    pip install PyQt6
    gui_frameworks+=("PyQt6")
else
    echo "Found GUI frameworks: ${gui_frameworks[*]}"
fi

# Run a quick test
echo "Running quick test..."
if python -c "from pyqt_preview import PreviewEngine; print('Import test passed')" 2>/dev/null; then
    echo "All systems go!"
else
    echo "ERROR: Import test failed"
    exit 1
fi

echo ""
echo "Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Run tests: pytest"
echo "  3. Try an example: pyqt-preview run examples/simple_app.py"
echo "  4. Check the CONTRIBUTING.md file for more information"
echo ""
echo "Happy coding!" 