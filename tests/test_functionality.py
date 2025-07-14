#!/usr/bin/env python3
"""
Comprehensive test suite for PyQt Preview.
Tests all major functionality to ensure the tool works correctly.
"""

import sys
import tempfile
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import all necessary modules
from pyqt_preview.cli import app
from pyqt_preview.compiler import UICompiler
from pyqt_preview.config import Config
from pyqt_preview.watcher import FileWatcher, PreviewFileHandler


def test_imports():
    """Test that all main modules can be imported."""
    print("Testing imports...")

    # The imports are now at the top of the file, so this test is redundant
    # but kept for consistency with the original file.
    print("All imports successful")
    assert True  # Always passes since imports at top succeeded


def test_config():
    """Test configuration loading and validation."""
    print("Testing configuration...")

    # Test default config
    config = Config()
    assert config.framework == "auto"
    assert config.reload_delay == 0.5
    assert config.preserve_window_state is True

    # Test config validation
    errors = config.validate()
    assert errors == [], f"Config validation errors: {errors}"

    # Test framework detection
    framework = config.detect_framework()
    assert framework in ["pyqt5", "pyqt6", "pyside2", "pyside6"]

    print("Configuration tests passed")


def test_ui_compiler():
    """Test UI compiler functionality."""
    print("Testing UI compiler...")

    config = Config()
    compiler = UICompiler(config)

    # Test compiler availability check
    compiler.check_compiler_available()

    # Test finding UI files (should not crash even if no files exist)
    ui_files = compiler.find_ui_files()
    assert isinstance(ui_files, list)

    # Test get_compiler_version (should not crash)
    compiler.get_compiler_version()
    # Version might be None if compiler is not available

    # Test output path generation
    test_ui_file = Path("test.ui")
    output_path = compiler.get_output_path(test_ui_file)
    assert output_path.suffix == ".py"

    print("UI compiler tests passed")


def test_file_watcher():
    """Test file watcher functionality."""
    print("Testing file watcher...")

    config = Config()

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        config.watch_dir = temp_dir

        # Test watcher creation
        def dummy_callback(filename):
            pass

        watcher = FileWatcher(config, dummy_callback)

        # Test that watcher can be created without errors
        assert watcher is not None

        # Test pattern matching
        handler = PreviewFileHandler(config, dummy_callback)

        # Test should_ignore_file method
        assert handler._should_ignore_file("test.pyc") is True
        assert handler._should_ignore_file("test.py") is False

    print("File watcher tests passed")


def test_cli():
    """Test CLI functionality."""
    print("Testing CLI...")

    # Test that the CLI app can be imported
    assert app is not None

    print("CLI tests passed")


def test_example_files():
    """Test that example files exist and are valid."""
    print("Testing example files...")

    examples_dir = Path(__file__).parent.parent / "examples"

    if not examples_dir.exists():
        print("Examples directory not found - skipping")
        return  # Skip the test if no examples directory

    # Check for example files
    example_files = list(examples_dir.glob("*.py"))

    if not example_files:
        print("No example files found - skipping")
        return  # Skip if no example files

    # Test that examples can be parsed (basic syntax check)
        for example_file in example_files:
            with open(example_file, encoding="utf-8") as f:
                content = f.read()            # This will raise SyntaxError if the file has syntax errors
            compile(content, str(example_file), "exec")

    print("Example files tests passed")


def main():
    """Run all tests."""
    print("PyQt Preview - Comprehensive Test Suite")
    print("=" * 50)

    tests = [
        test_imports,
        test_config,
        test_ui_compiler,
        test_file_watcher,
        test_cli,
        test_example_files,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except (AssertionError, SyntaxError, ImportError, OSError) as e:
            print(f"Test {test_func.__name__} crashed: {e}")
            failed += 1

        print("-" * 30)

    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("All tests passed! PyQt Preview is working correctly.")
        return 0
    print("Some tests failed. Please check the output above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
