@echo off
REM Development setup script for PyQt Preview (Windows)

echo Setting up PyQt Preview development environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python detected
python --version

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install development dependencies
echo Installing PyQt Preview in development mode...
pip install -e ".[dev]"

REM Verify installation
echo Verifying installation...
pyqt-preview --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Installation verification failed
    pause
    exit /b 1
) else (
    echo PyQt Preview installed successfully!
    pyqt-preview --version
)

REM Check for GUI frameworks
echo Checking GUI frameworks...
python -c "import PyQt6" >nul 2>&1
if not errorlevel 1 (
    echo PyQt6 found
    set GUI_FOUND=1
)

python -c "import PyQt5" >nul 2>&1
if not errorlevel 1 (
    echo PyQt5 found
    set GUI_FOUND=1
)

python -c "import PySide6" >nul 2>&1
if not errorlevel 1 (
    echo PySide6 found
    set GUI_FOUND=1
)

python -c "import PySide2" >nul 2>&1
if not errorlevel 1 (
    echo PySide2 found
    set GUI_FOUND=1
)

if not defined GUI_FOUND (
    echo WARNING: No GUI frameworks detected. Installing PyQt6...
    pip install PyQt6
)

REM Run a quick test
echo Running quick test...
python -c "from pyqt_preview import PreviewEngine; print('Import test passed')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Import test failed
    pause
    exit /b 1
) else (
    echo All systems go!
)

echo.
echo Development environment setup complete!
echo.
echo Next steps:
echo   1. Activate the environment: venv\Scripts\activate.bat
echo   2. Run tests: pytest
echo   3. Try an example: pyqt-preview run examples/simple_app.py
echo   4. Check the CONTRIBUTING.md file for more information
echo.
echo Happy coding!
pause 