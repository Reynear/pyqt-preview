# Changelog

All notable changes to PyQt Preview will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-XX

### Added
- Development infrastructure for source builds
- Comprehensive CONTRIBUTING.md with development guidelines
- Development setup scripts (setup-dev.sh, setup-dev.bat)
- Separate dependency groups for dev, test, and build
- Enhanced documentation structure with tutorials and guides
- Cross-platform development setup automation

### Major Simplification  
This release transforms PyQt Preview from a production-ready tool to a focused development tool.

### Removed
- Health monitoring system (health.py deleted)
- Complex security features (process isolation, resource limits)
- Structured JSON logging (simplified to console logging)
- Production-ready configuration settings
- Performance monitoring and restart limits

### Simplified
- Security module: 300+ lines → 80 lines (basic validation only)
- Logging system: 400+ lines → 40 lines (simple console output)
- Core engine: 550+ lines → 250 lines (removed monitoring integration)
- Configuration: removed production settings and constraints

### Changed
- Project status: Production/Stable → Development Status :: 3 - Alpha
- Dependencies: removed psutil, added pyqt5>=5.15.11
- Documentation: simplified from enterprise marketing to development tool focus
- Version: Updated to development status (0.2.0)

## [0.1.0] - 2025-01-XX

### Added
- Live reloading for PyQt5/PyQt6 applications
- Automatic .ui file compilation
- File watching with configurable patterns
- Window state preservation across reloads
- CLI interface with typer and rich
- Configuration system with TOML support
- Cross-platform compatibility (Windows, macOS, Linux)
- Comprehensive examples and documentation
- Test suite with pytest

### Features
- `pyqt-preview run` command for live preview
- `pyqt-preview init` command for project setup
- `pyqt-preview check` command for system validation
- Support for PyQt5, PyQt6, PySide2, and PySide6
- Configurable reload delays and ignore patterns
- Verbose logging and error reporting
- Batch file change processing
- Graceful process termination

