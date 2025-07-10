# Contributing to PyQt Preview

### Feature Requests

1. **Check existing issues** first to avoid duplicates
2. **Describe the use case** - what problem does it solve?
3. **Provide examples** - show how it would work
4. **Consider the scope** - is it aligned with PyQt Preview's goals?
5. **Be patient** - not all features will be implemented immediately

### Prerequisites

- Python 3.8+ 
- Git
- One of: PyQt5, PyQt6, PySide2, or PySide6

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/pyqt-preview.git
   cd pyqt-preview
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install in Development Mode**
   ```bash
   # Install with all development dependencies
   pip install -e ".[dev]"
   
   # Or install minimal dependencies
   pip install -e .
   ```

4. **Verify Installation**
   ```bash
   pyqt-preview --version
   pyqt-preview check
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=pyqt_preview --cov-report=html

# Run specific test files
pytest tests/test_config.py
pytest tests/test_watcher.py

# Run tests for specific functionality
pytest -k "test_config"
```

### Code Quality Checks

```bash
# Format code (run before committing)
black src/ tests/ examples/
isort src/ tests/ examples/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Run all quality checks
black --check src/ tests/
isort --check-only src/ tests/
mypy src/
flake8 src/ tests/
```

### Testing Your Changes

```bash
# Test with different frameworks
export PYQT_PREVIEW_FRAMEWORK=pyqt6
python examples/simple_app.py

# Test CLI commands
pyqt-preview run examples/simple_app.py --verbose
pyqt-preview init --framework pyqt5
pyqt-preview check
```

### Building and Distribution

```bash
# Build distribution packages
python -m build

# Check the built packages
twine check dist/*

# Install from local build (for testing)
pip install dist/pyqt_preview-*.whl
```

## Code Style Guidelines

### Python Style
- Follow PEP 8
- Use Black for formatting (line length: 88)
- Use isort for import sorting
- Add type hints for all public functions
- Use descriptive variable and function names

### Code Structure
- Keep functions focused and small
- Use dataclasses for configuration objects
- Prefer composition over inheritance
- Add docstrings for public classes and methods

### Example Code Style
```python
from typing import Optional, List
from pathlib import Path

def validate_script_path(script_path: Path, allowed_extensions: Optional[List[str]] = None) -> Path:
    """
    Validate that a script path is safe and accessible.
    
    Args:
        script_path: Path to the Python script
        allowed_extensions: List of allowed file extensions
        
    Returns:
        Validated and resolved path
        
    Raises:
        SecurityError: If path validation fails
    """
    if allowed_extensions is None:
        allowed_extensions = ['.py']
    
    # Implementation here
    return script_path.resolve()
```

## Testing Guidelines

### Writing Tests
- Use pytest for all tests
- Write tests for both success and failure cases
- Mock external dependencies (file system, subprocesses)
- Use descriptive test names

### Test Structure
```python
def test_config_validation_with_invalid_framework():
    """Test that config validation fails with invalid framework."""
    config = Config(framework="invalid")
    errors = config.validate()
    assert len(errors) > 0
    assert "framework" in errors[0].lower()
```

### Test Coverage
- Aim for >90% test coverage
- Focus on critical paths and edge cases
- Test configuration combinations
- Test cross-platform compatibility when possible

## Pull Request Process

### Before Submitting
1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, tested code
   - Follow the style guidelines
   - Update documentation if needed

3. **Run quality checks**
   ```bash
   black src/ tests/
   isort src/ tests/
   mypy src/
   flake8 src/ tests/
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

### Submitting the PR
1. Push your branch to your fork
2. Create a pull request on GitHub
3. Fill out the PR template
4. Wait for review and address feedback

### PR Requirements
- All tests must pass
- Code coverage should not decrease
- Documentation should be updated if needed
- Commit messages should be clear and descriptive

## Development Environments

### VS Code Setup
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true
}
```

### PyCharm Setup
- Set Python interpreter to `./venv/bin/python`
- Enable Black as code formatter
- Configure pytest as test runner
- Enable type checking

## Debugging

### Common Issues
- **Import errors**: Make sure you installed with `-e .` flag
- **Framework not found**: Install PyQt/PySide packages
- **Tests failing**: Check if you're in the right virtual environment

### Debug Mode
```bash
# Run with verbose logging
pyqt-preview run examples/simple_app.py --verbose

# Debug file watching
export PYQT_PREVIEW_DEBUG=1
pyqt-preview run examples/simple_app.py
```

## Project Structure

```
pyqt-preview/
├── src/pyqt_preview/         # Main package
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Command-line interface
│   ├── core.py               # Core preview engine
│   ├── config.py             # Configuration management
│   ├── watcher.py            # File watching
│   ├── compiler.py           # UI compilation
│   ├── security.py           # Basic validation
│   └── logging_config.py     # Simple logging
├── tests/                    # Test suite
├── examples/                 # Example applications
├── docs/                     # Documentation
├── LICENSE                   # MIT License
├── README.md                 # Project overview
├── TUTORIAL.md               # Quick start guide
├── CONTRIBUTING.md           # This file
└── pyproject.toml            # Project configuration
```

## Feature Requests and Issues

### Bug Reports
1. **Check existing issues** first to avoid duplicates
2. **Provide reproduction steps** - minimal example that shows the bug
3. **Include system information** - Python version, OS, PyQt version
4. **Describe expected vs actual behavior**
5. **Add error messages** - full stack traces help

### Feature Requests
1. **Check existing issues** first to avoid duplicates
2. **Describe the use case** - what problem does it solve?
3. **Provide examples** - show how it would work
4. **Consider the scope** - is it aligned with PyQt Preview's goals?
5. **Be patient** - not all features will be implemented immediately

We welcome feature suggestions that enhance the live reload experience for PyQt development.

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check the docs/ directory
- **Examples**: Look at the examples/ directory for usage patterns

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PyQt Preview!
