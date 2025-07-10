# PyQt Preview Test Suite

This directory contains the comprehensive test suite for PyQt Preview.

## Test Structure

### Unit Tests
- **`test_cli.py`** - CLI commands and argument parsing tests (23 tests)
- **`test_config.py`** - Configuration system tests (enhanced coverage)
- **`test_core.py`** - Core engine and process management tests (32 tests)
- **`test_compiler.py`** - UI compiler functionality tests (26 tests)
- **`test_security.py`** - File validation and security tests (26 tests)
- **`test_logging_config.py`** - Logging configuration tests (19 tests)
- **`test_watcher.py`** - File watching functionality tests (enhanced coverage)

### Integration Tests
- **`test_functionality.py`** - High-level functionality tests for all core components (6 tests)

### Test Configuration
- **`conftest.py`** - Pytest configuration and shared fixtures

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
# Unit tests
pytest tests/test_cli.py          # CLI functionality
pytest tests/test_config.py       # Configuration system
pytest tests/test_core.py         # Core engine components
pytest tests/test_compiler.py     # UI compiler
pytest tests/test_security.py     # Security validation
pytest tests/test_logging_config.py # Logging setup
pytest tests/test_watcher.py      # File watching

# Integration tests
pytest tests/test_functionality.py
```

### Run with Coverage
```bash
pytest --cov=pyqt_preview --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Categories

### CLI Tests (`test_cli.py`)
- Command-line argument parsing
- Run, init, and check commands
- Configuration integration
- Error handling and user interaction
- Version display and help text

### Core Engine Tests (`test_core.py`)
- Window state persistence
- Process lifecycle management
- Preview engine orchestration
- File change handling
- Graceful shutdown and cleanup

### Compiler Tests (`test_compiler.py`)
- UI file discovery and compilation
- Framework-specific compiler detection
- Output path generation
- Error handling and timeouts
- Dependency tracking

### Security Tests (`test_security.py`)
- File path validation
- Security error handling
- Symlink and permission checks
- Case sensitivity handling
- Path traversal prevention

### Logging Tests (`test_logging_config.py`)
- Logging setup and configuration
- Verbose/non-verbose modes
- Handler management
- Formatter configuration
- Logger hierarchy

### Configuration Tests (`test_config.py`)
- Configuration loading and validation
- Framework detection
- Default values and overrides
- TOML file parsing
- Error handling and validation

### File Watcher Tests (`test_watcher.py`)
- File change detection
- Pattern matching and filtering
- Debouncing behavior
- Context manager functionality
- Observer lifecycle management

### Integration Tests (`test_functionality.py`)
- Import validation
- End-to-end functionality
- Component integration
- Example files verification

## Test Requirements

- **pytest** - Test framework
- **PyQt6** or **PyQt5** - GUI framework for testing
- **watchdog** - File watching dependency

## Development Testing

For quick development testing without pytest:

```bash
# Run functionality tests directly
python tests/test_functionality.py
```

## Test Statistics

**Total: 172 tests** covering all source modules with comprehensive scenarios:
- Success paths and error conditions
- Edge cases and boundary conditions
- Security validations
- Performance and timing behavior
- Integration between components

## Notes

- Some tests require PyQt/PySide to be installed
- File watcher tests create temporary directories
- All tests clean up after themselves automatically
- Tests use extensive mocking for isolated unit testing
- Real file operations are tested in temporary directories
- 100% pass rate with zero tolerance for failures 