"""
Comprehensive tests for PyQt Preview security module.
"""

import tempfile
from pathlib import Path

import pytest

from pyqt_preview.security import SecurityError, validate_python_file, validate_ui_file


class TestSecurityError:
    """Test cases for SecurityError exception."""

    def test_security_error_is_exception(self):
        """Test that SecurityError is a proper exception."""
        assert issubclass(SecurityError, Exception)

    def test_security_error_with_message(self):
        """Test SecurityError with custom message."""
        message = "Test security error"
        error = SecurityError(message)
        assert str(error) == message

    def test_security_error_can_be_raised(self):
        """Test that SecurityError can be raised and caught."""
        with pytest.raises(SecurityError) as exc_info:
            raise SecurityError("Test error")
        assert "Test error" in str(exc_info.value)


class TestValidatePythonFile:
    """Test cases for validate_python_file function."""

    def test_validate_python_file_valid_string_path(self):
        """Test validating a valid Python file with string path."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('Hello, World!')")
            file_path = f.name

        try:
            result = validate_python_file(file_path)
            assert isinstance(result, Path)
            assert result.suffix == ".py"
            assert result.is_absolute()
        finally:
            Path(file_path).unlink()

    def test_validate_python_file_valid_path_object(self):
        """Test validating a valid Python file with Path object."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('Hello, World!')")
            file_path = Path(f.name)

        try:
            result = validate_python_file(file_path)
            assert isinstance(result, Path)
            assert result.suffix == ".py"
            assert result.is_absolute()
        finally:
            file_path.unlink()

    def test_validate_python_file_non_python_extension(self):
        """Test validating file with non-Python extension."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Not Python code")
            file_path = f.name

        try:
            with pytest.raises(SecurityError) as exc_info:
                validate_python_file(file_path)
            assert "must be a Python file" in str(exc_info.value)
            assert file_path in str(exc_info.value)
        finally:
            Path(file_path).unlink()

    def test_validate_python_file_uppercase_extension(self):
        """Test validating file with uppercase .PY extension."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".PY", delete=False) as f:
            f.write("print('Hello')")
            file_path = f.name

        try:
            # Should work with uppercase extension
            result = validate_python_file(file_path)
            assert isinstance(result, Path)
        finally:
            Path(file_path).unlink()

    def test_validate_python_file_no_extension(self):
        """Test validating file with no extension."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("print('Hello')")
            file_path = f.name

        try:
            with pytest.raises(SecurityError) as exc_info:
                validate_python_file(file_path)
            assert "must be a Python file" in str(exc_info.value)
        finally:
            Path(file_path).unlink()

    def test_validate_python_file_nonexistent(self):
        """Test validating nonexistent Python file."""
        nonexistent_path = "/nonexistent/script.py"

        with pytest.raises(SecurityError) as exc_info:
            validate_python_file(nonexistent_path)
        assert "does not exist" in str(exc_info.value)
        assert "script.py" in str(exc_info.value)


    def test_validate_ui_file_directory(self):
        """Test validating directory instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory with .ui extension
            dir_path = Path(temp_dir) / "form.ui"
            dir_path.mkdir()

            try:
                with pytest.raises(SecurityError) as exc_info:
                    validate_ui_file(str(dir_path))
                assert "not a file" in str(exc_info.value)
            finally:
                pass  # Directory will be cleaned up by TemporaryDirectory

    def test_validate_ui_file_returns_resolved_path(self):
        """Test that validate_ui_file returns resolved absolute path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a UI file
            file_path = Path(temp_dir) / "form.ui"
            file_path.write_text('<?xml version="1.0" encoding="UTF-8"?><ui></ui>')

            # Use relative path if possible
            relative_path = file_path.relative_to(Path.cwd()) if file_path.is_relative_to(Path.cwd()) else file_path

            result = validate_ui_file(str(relative_path))

            assert result.is_absolute()
            assert result.exists()
            assert result == file_path.resolve()

    def test_validate_ui_file_different_content(self):
        """Test that UI file validation doesn't check content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ui", delete=False) as f:
            # Write invalid UI content - should still pass validation
            f.write("This is not valid UI XML content")
            file_path = f.name

        try:
            # Should still pass - we only validate file path, not content
            result = validate_ui_file(file_path)
            assert isinstance(result, Path)
            assert result.suffix == ".ui"
        finally:
            Path(file_path).unlink()


class TestSecurityIntegration:
    """Integration tests for security module functions."""

    def test_both_validators_with_same_file_different_extensions(self):
        """Test both validators with files that have correct/incorrect extensions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python file
            py_file = Path(temp_dir) / "script.py"
            py_file.write_text("print('Hello')")

            # Create UI file
            ui_file = Path(temp_dir) / "form.ui"
            ui_file.write_text('<?xml version="1.0"?><ui></ui>')

            # Python file should validate as Python but not as UI
            python_result = validate_python_file(py_file)
            assert python_result.suffix == ".py"

            with pytest.raises(SecurityError):
                validate_ui_file(py_file)

            # UI file should validate as UI but not as Python
            ui_result = validate_ui_file(ui_file)
            assert ui_result.suffix == ".ui"

            with pytest.raises(SecurityError):
                validate_python_file(ui_file)

    def test_validators_handle_edge_case_filenames(self):
        """Test validators with edge case filenames."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Files with multiple dots
            py_file = Path(temp_dir) / "my.script.test.py"
            py_file.write_text("print('test')")

            ui_file = Path(temp_dir) / "my.form.test.ui"
            ui_file.write_text("<ui></ui>")

            # Should work correctly
            assert validate_python_file(py_file).name == "my.script.test.py"
            assert validate_ui_file(ui_file).name == "my.form.test.ui"

    def test_validators_with_symlinks(self):
        """Test validators with symbolic links (if supported by OS)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create actual file
            actual_file = Path(temp_dir) / "script.py"
            actual_file.write_text("print('Hello')")

            try:
                # Create symlink
                symlink_file = Path(temp_dir) / "link.py"
                symlink_file.symlink_to(actual_file)

                # Both should validate and resolve to different paths
                actual_result = validate_python_file(actual_file)
                symlink_result = validate_python_file(symlink_file)

                assert actual_result.exists()
                assert symlink_result.exists()
                # Resolved paths should point to the same file
                assert actual_result.samefile(symlink_result)

            except OSError:
                # Symlinks might not be supported on all systems
                pytest.skip("Symbolic links not supported on this system")
