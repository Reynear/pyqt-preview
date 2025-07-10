# PyQt Preview - Technical Architecture Guide

## Overview

This document explains the technical architecture, design decisions, and implementation details of PyQt Preview. For usage tutorials, see [Getting Started](tutorials/getting-started.md).

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
│                    PyQt Preview System                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   CLI       │    │   Config    │    │   Watcher   │     │
│  │ (cli.py)    │◄──►│ (config.py) │◄──►│(watcher.py) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Engine    │    │  Compiler   │    │   Process   │     │
│  │ (core.py)   │◄──►│(compiler.py)│◄──►│ Management  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  PyQt Process   │
                    │   (External)    │
                    └─────────────────┘
```

## Core Components Deep Dive

### 1. Configuration System (`config.py`)

**Purpose**: Centralized configuration management with validation and defaults.

**Key Design Decisions**:
- **TOML-based**: Human-readable, supports nested structures
- **Validation**: Runtime type checking and constraint validation
- **Merging Strategy**: File config + CLI args + defaults
- **Framework Detection**: Automatic detection of available Qt frameworks

**Implementation Details**:

```python
@dataclass
class Config:
    framework: str = "auto"
    ui_compiler: str = "auto"
    watch_patterns: List[str] = field(default_factory=lambda: ["*.py", "*.ui"])
    ignore_patterns: List[str] = field(default_factory=lambda: ["__pycache__", "*.pyc"])
    reload_delay: float = 0.5
    preserve_window_state: bool = True
    
    def validate(self) -> List[str]:
        """Validate configuration and return error messages."""
        errors = []
        
        # Framework validation
        if self.framework not in ["auto", "pyqt5", "pyqt6", "pyside2", "pyside6"]:
            errors.append(f"Invalid framework: {self.framework}")
        
        # Delay validation
        if self.reload_delay < 0.1:
            errors.append("Reload delay must be >= 0.1 seconds")
        
        return errors
    
    def get_ui_compiler_command(self) -> str:
        """Determine the appropriate UI compiler command."""
        if self.ui_compiler != "auto":
            return self.ui_compiler
        
        # Auto-detection logic
        framework = self.detect_framework()
        return {
            "pyqt5": "pyuic5",
            "pyqt6": "pyuic6", 
            "pyside2": "pyside2-uic",
            "pyside6": "pyside6-uic"
        }.get(framework, "pyuic6")
```

### 2. File Watcher (`watcher.py`)

**Purpose**: Cross-platform file system monitoring with intelligent filtering.

**Key Design Decisions**:
- **watchdog Library**: Cross-platform, efficient file system events
- **Debouncing**: Prevents rapid-fire reloads from multiple saves
- **Pattern Matching**: Configurable include/exclude patterns
- **Event Batching**: Groups related file changes

**Implementation Details**:

```python
class FileWatcher:
    def __init__(self, config: Config):
        self.config = config
        self.observer = Observer()
        self.debounce_timer = None
        self.pending_changes = set()
    
    def _should_watch_file(self, file_path: Path) -> bool:
        """Determine if a file should be watched based on patterns."""
        # Check ignore patterns first (higher priority)
        for pattern in self.config.ignore_patterns:
            if fnmatch.fnmatch(str(file_path), pattern):
                return False
        
        # Check watch patterns
        for pattern in self.config.watch_patterns:
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
        
        return False
    
    def _on_file_change(self, event):
        """Handle file system change events with debouncing."""
        if not self._should_watch_file(Path(event.src_path)):
            return
        
        self.pending_changes.add(event.src_path)
        
        # Cancel existing timer
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        # Start new debounce timer
        self.debounce_timer = Timer(self.config.reload_delay, self._process_changes)
        self.debounce_timer.start()
    
    def _process_changes(self):
        """Process all pending changes after debounce period."""
        if self.pending_changes:
            self.callback(list(self.pending_changes))
            self.pending_changes.clear()
```

### 3. UI Compiler (`compiler.py`)

**Purpose**: Automatic compilation of Qt Designer UI files to Python code.

**Key Design Decisions**:
- **Subprocess Execution**: Isolated compilation process
- **Dependency Tracking**: Only recompile when UI file is newer
- **Error Handling**: Graceful failure with user feedback
- **Output Management**: Configurable output directories

**Implementation Details**:

```python
class UICompiler:
    def __init__(self, config: Config):
        self.config = config
        self.compiler_cmd = config.get_ui_compiler_command()
    
    def compile_ui_file(self, ui_file: Path) -> CompilationResult:
        """Compile a UI file to Python code."""
        output_file = self._get_output_path(ui_file)
        
        # Check if recompilation is needed
        if not self._needs_recompilation(ui_file, output_file):
            return CompilationResult(success=True, message="No changes detected")
        
        try:
            # Build compilation command
            cmd = [
                self.compiler_cmd,
                str(ui_file),
                "-o", str(output_file)
            ]
            
            # Execute compilation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # Prevent hanging
                check=True
            )
            
            return CompilationResult(
                success=True,
                message=f"Compiled {ui_file.name} -> {output_file.name}"
            )
            
        except subprocess.TimeoutExpired:
            return CompilationResult(
                success=False,
                message=f"Compilation timeout for {ui_file.name}"
            )
        except subprocess.CalledProcessError as e:
            return CompilationResult(
                success=False,
                message=f"Compilation failed: {e.stderr}"
            )
    
    def _needs_recompilation(self, ui_file: Path, output_file: Path) -> bool:
        """Check if UI file needs recompilation."""
        if not output_file.exists():
            return True
        
        return ui_file.stat().st_mtime > output_file.stat().st_mtime
```

### 4. Process Management

**Purpose**: Lifecycle management of PyQt application processes.

**Key Design Decisions**:
- **Process Isolation**: Each app runs in separate process
- **Graceful Termination**: Proper cleanup on reload
- **State Preservation**: Window geometry and application state
- **Error Recovery**: Automatic restart on crashes

**Implementation Details**:

```python
class PreviewProcess:
    def __init__(self, script_path: str, config: Config):
        self.script_path = script_path
        self.config = config
        self.process = None
        self.state_file = None
    
    def start(self) -> bool:
        """Start the PyQt application process."""
        try:
            # Save current window state if process exists
            if self.process and self.config.preserve_window_state:
                self._save_window_state()
            
            # Terminate existing process
            if self.process:
                self._terminate_process()
            
            # Prepare environment
            env = os.environ.copy()
            if self.config.preserve_window_state and self.state_file:
                env['PYQT_PREVIEW_GEOMETRY'] = self._load_window_state()
            
            # Start new process
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to start process: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart the application process."""
        return self.start()
    
    def _terminate_process(self):
        """Gracefully terminate the current process."""
        if not self.process:
            return
        
        try:
            # Try graceful termination first
            self.process.terminate()
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if graceful termination fails
            self.process.kill()
            self.process.wait()
```

### 5. Preview Engine (`core.py`)

**Purpose**: Orchestrates all components and manages the live reload workflow.

**Key Design Decisions**:
- **Event Coordination**: Manages interactions between components
- **Error Isolation**: Failures in one component don't crash the system
- **Performance Optimization**: Efficient resource usage
- **User Feedback**: Clear status messages and progress indicators

**Implementation Details**:

```python
class PreviewEngine:
    def __init__(self, config: Config):
        self.config = config
        self.watcher = FileWatcher(config)
        self.compiler = UICompiler(config)
        self.process_manager = None
        self.reload_count = 0
        self.is_running = False
    
    def start(self, script_path: str) -> bool:
        """Start the live preview system."""
        try:
            # Initialize process manager
            self.process_manager = PreviewProcess(script_path, self.config)
            
            # Start file watcher
            self.watcher.start(self._on_file_change)
            
            # Start initial application
            if not self.process_manager.start():
                return False
            
            self.is_running = True
            return True
            
        except Exception as e:
            print(f"Failed to start preview engine: {e}")
            return False
    
    def _on_file_change(self, changed_files: List[str]):
        """Handle file change events."""
        try:
            # Handle UI compilation first
            for file_path in changed_files:
                if file_path.endswith('.ui'):
                    result = self.compiler.handle_file_change(file_path)
                    if not result.success:
                        print(f"UI compilation failed: {result.message}")
            
            # Restart application
            if self.process_manager.restart():
                self.reload_count += 1
                print(f"Reload #{self.reload_count} completed")
            else:
                print("Failed to restart application")
                
        except Exception as e:
            print(f"Error handling file change: {e}")
```

## Design Patterns Used

### 1. Observer Pattern
- **Usage**: File watcher notifies engine of changes
- **Benefits**: Loose coupling between components
- **Implementation**: Callback-based event system

### 2. Strategy Pattern
- **Usage**: Different UI compilers for different frameworks
- **Benefits**: Easy to add new framework support
- **Implementation**: Configurable compiler selection

### 3. Factory Pattern
- **Usage**: Creating appropriate UI compilers and process managers
- **Benefits**: Encapsulates object creation logic
- **Implementation**: Factory methods in configuration system

### 4. State Pattern
- **Usage**: Managing different states of the preview system
- **Benefits**: Clear state transitions and behavior
- **Implementation**: State machine for process lifecycle

## Performance Considerations

### 1. File System Monitoring
- **Debouncing**: Prevents excessive reloads from rapid saves
- **Pattern Filtering**: Only watch relevant files
- **Event Batching**: Group related changes

### 2. Process Management
- **Resource Cleanup**: Proper termination to prevent zombie processes
- **State Preservation**: Window geometry preserved across reloads

### 3. UI Compilation
- **Dependency Tracking**: Only recompile when necessary
- **Timeout Protection**: Prevent hanging compilation processes
- **Error Recovery**: Graceful handling of compilation failures

## Error Handling Strategy

### 1. Graceful Degradation
- UI compilation failures don't stop the system
- Process crashes trigger automatic restart
- Configuration errors show helpful messages

### 2. User Feedback
- Clear error messages with actionable advice
- Progress indicators for long operations
- Verbose mode for debugging

### 3. Recovery Mechanisms
- Automatic retry for transient failures
- Fallback to default configurations
- State preservation across errors

## Security Considerations

PyQt Preview implements basic security measures:

### 1. File Path Validation
- Basic validation of Python and UI file paths
- Pattern-based filtering for watched files
- Protection against path traversal attacks

### 2. Process Isolation
- Each application runs in separate process
- No shared memory between processes
- Timeout protection against hanging processes

## Testing Strategy

### 1. Unit Testing
- Individual component testing
- Mock file system events
- Configuration validation tests

### 2. Integration Testing
- End-to-end workflow testing
- Cross-platform compatibility
- Framework detection testing

### 3. Performance Testing
- File system monitoring performance
- Process startup/shutdown timing
- Memory usage profiling

## Conclusion

PyQt Preview's architecture prioritizes:

1. **Reliability**: Robust error handling and recovery
2. **Performance**: Efficient resource usage and minimal overhead
3. **Extensibility**: Clean interfaces for future enhancements
4. **User Experience**: Smooth workflow with clear feedback

The modular design allows for easy maintenance and feature additions while maintaining the core live reload functionality that makes PyQt development more efficient and enjoyable.
