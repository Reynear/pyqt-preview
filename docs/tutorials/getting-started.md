# PyQt Preview - Advanced User Tutorial

This guide is designed for PyQt users who already have experience building applications and want to integrate PyQt Preview for rapid development and live reload workflows.

## Integrating PyQt Preview into Existing Projects

PyQt Preview can be added to any mature PyQt project with minimal changes. Simply install the package and use the CLI to run your main application script:

```bash
pyqt-preview run your_app.py
```

For complex projects, you can use a TOML config file to specify custom entry points, UI directories, reload delays, and ignore patterns. See the examples and documentation for advanced config options.

**Best Practices:**
- Organize your project with clear separation between UI, logic, and resources.
- Use absolute imports and ensure your PYTHONPATH is set correctly for module reloads.
- For multi-window apps, consider how state and geometry are preserved across reloads (see platform notes below).

## Live Reload in Complex Applications

PyQt Preview supports live reload for applications with multiple windows, custom widgets, and modular architectures. State preservation and window focus behavior can be configured:
- Use `--preserve-state` to keep window geometry across reloads.
- On macOS, use `--keep-window-focus` to prevent the preview window from stealing focus.
- On Windows and Linux, focus restoration is not supported due to OS limitations.

**Tips:**
- Minimize global state and use signals/slots for communication between components.
- Structure your app to allow safe reloads without side effects.

## Qt Designer and UI Compilation

For projects using Qt Designer, PyQt Preview will automatically compile `.ui` files to Python classes on save. You can specify a custom UI directory and import compiled classes as needed.

**Advanced Usage:**
- Support for multiple UI files and custom UI directories.
- Integrate compiled UI classes with your existing architecture.
- Handle dynamic UI changes and custom widgets seamlessly.

## Advanced Configuration

Customize PyQt Preview for your workflow using TOML config files and CLI flags:
- Set custom file patterns and ignore rules for large projects.
- Adjust reload delays to optimize performance.
- Use environment variables for advanced control.

**Example TOML config:**
```toml
entry_point = "your_app.py"
ui_dir = "ui/"
reload_delay = 1.0
ignore = ["tests/*", "docs/*"]
preserve_state = true
keep_window_focus = true
```

## Troubleshooting for Advanced Users

- **Import errors after reload:** Check your PYTHONPATH and use absolute imports.
- **UI compiler not found:** Install the appropriate Qt tools (`pyuic6`, `pyuic5`, etc.).
- **Performance issues:** Increase reload delay and refine ignore patterns.
- **Complex reload bugs:** Refactor code to minimize side effects and global state.

## Best Practices and Workflow Tips

- Integrate PyQt Preview with your preferred IDE/editor for seamless development.
- Use modular project layouts for maintainability and easier reloads.
- Share config files and workflow tips with your team for consistency.

## Conclusion and Next Steps

With PyQt Preview, experienced PyQt developers can dramatically speed up UI iteration and workflow. Explore advanced features, experiment with configuration, and integrate with your existing projects for maximum productivity.

**Further Resources:**
- [Main README](../README.md)
- [Architecture Guide](../guides/architecture-guide.md)
- [Example Projects](../../examples/)

**Happy coding with PyQt Preview!**
