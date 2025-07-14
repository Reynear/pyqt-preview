# PyQt Preview - Technical Architecture Guide

## Overview

This document explains the technical architecture, design decisions, and implementation details of PyQt Preview. For usage tutorials, see [Getting Started](../tutorials/getting-started.md).

## System Architecture

### High-Level Design

PyQt Preview follows a **reactive architecture** with these core principles:

1. **Event-Driven**: File system events trigger the reload pipeline
2. **Separation of Concerns**: Each component has a single responsibility
3. **Fault Tolerance**: Graceful handling of compilation and runtime errors
4. **Cross-Platform**: Consistent behavior across Windows, macOS, and Linux

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PyQt Preview System                     │
├───────────────┬───────────────┬───────────────┬─────────────┤
│   CLI         │   Config      │   Watcher     │             │
│ (cli.py)      │ (config.py)   │ (watcher.py)  │             │
│               │               │               │             │
│   Engine      │  Compiler     │   Process     │             │
│ (core.py)     │ (compiler.py) │ Management    │             │
│               │               │               │             │
└───────────────┴───────────────┴───────────────┴─────────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │  PyQt Process       │
                      │   (External)        │
                      └─────────────────────┘
```

## Core Components Deep Dive

### 1. Configuration System (`config.py`)

- **TOML-based**: Human-readable, supports nested structures
- **Validation**: Runtime type checking and constraint validation
- **Merging Strategy**: File config + CLI args + defaults
- **Framework Detection**: Automatic detection of available Qt frameworks

### 2. File Watcher (`watcher.py`)

- **watchdog Library**: Cross-platform, efficient file system events
- **Debouncing**: Prevents rapid-fire reloads from multiple saves
- **Pattern Matching**: Configurable include/exclude patterns
- **Event Batching**: Groups related file changes

### 3. UI Compiler (`compiler.py`)

- **Subprocess Execution**: Isolated compilation process
- **Dependency Tracking**: Only recompile when UI file is newer
- **Error Handling**: Graceful failure with user feedback
- **Output Management**: Configurable output directories

### 4. Process Management

- **Process Isolation**: Each app runs in separate process
- **Graceful Termination**: Proper cleanup on reload
- **State Preservation**: Window geometry and application state
- **Error Recovery**: Automatic restart on crashes

### 5. Preview Engine (`core.py`)

- **Event Coordination**: Manages interactions between components
- **Error Isolation**: Failures in one component don't crash the system
- **Performance Optimization**: Efficient resource usage
- **User Feedback**: Clear status messages and progress indicators

## Design Patterns Used

- **Observer Pattern**: File watcher notifies engine of changes
- **Strategy Pattern**: Different UI compilers for different frameworks
- **Factory Pattern**: Creating appropriate UI compilers and process managers
- **State Pattern**: Managing different states of the preview system

## Performance Considerations

- **Debouncing**: Prevents excessive reloads from rapid saves
- **Pattern Filtering**: Only watch relevant files
- **Event Batching**: Group related changes
- **Resource Cleanup**: Proper termination to prevent zombie processes
- **State Preservation**: Window geometry preserved across reloads
- **Dependency Tracking**: Only recompile when necessary
- **Timeout Protection**: Prevent hanging compilation processes
- **Error Recovery**: Graceful handling of compilation failures

## Error Handling Strategy

- **Graceful Degradation**: UI compilation failures don't stop the system; process crashes trigger automatic restart; configuration errors show helpful messages
- **User Feedback**: Clear error messages with actionable advice; progress indicators for long operations; verbose mode for debugging
- **Recovery Mechanisms**: Automatic retry for transient failures; fallback to default configurations; state preservation across errors

## Security Considerations

- **File Path Validation**: Basic validation of Python and UI file paths; pattern-based filtering for watched files; protection against path traversal attacks
- **Process Isolation**: Each application runs in separate process; no shared memory between processes; timeout protection against hanging processes

## Testing Strategy

- **Unit Testing**: Individual component testing; mock file system events; configuration validation tests
- **Integration Testing**: End-to-end workflow testing; cross-platform compatibility; framework detection testing
- **Performance Testing**: File system monitoring performance; process startup/shutdown timing; memory usage profiling

## Conclusion

PyQt Preview's architecture prioritizes:
1. **Reliability**: Robust error handling and recovery
2. **Performance**: Efficient resource usage and minimal overhead
3. **Extensibility**: Clean interfaces for future enhancements
4. **User Experience**: Smooth workflow with clear feedback

The modular design allows for easy maintenance and feature additions while maintaining the core live reload functionality that makes PyQt development more efficient and enjoyable.
