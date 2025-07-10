"""
Comprehensive tests for PyQt Preview logging configuration module.
"""

import io
import logging
import sys
from unittest.mock import Mock, patch

from pyqt_preview.logging_config import get_logger, setup_logging


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def teardown_method(self):
        """Clean up logging configuration after each test."""
        # Reset root logger to default state
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)

    def test_setup_logging_default_non_verbose(self):
        """Test setup_logging with default (non-verbose) settings."""
        setup_logging(verbose=False)

        root_logger = logging.getLogger()

        # Check level is INFO
        assert root_logger.level == logging.INFO

        # Check that there's exactly one handler
        assert len(root_logger.handlers) == 1

        # Check that it's a StreamHandler
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stdout

    def test_setup_logging_verbose(self):
        """Test setup_logging with verbose=True."""
        setup_logging(verbose=True)

        root_logger = logging.getLogger()

        # Check level is DEBUG
        assert root_logger.level == logging.DEBUG

        # Check that there's exactly one handler
        assert len(root_logger.handlers) == 1

        # Check that it's a StreamHandler
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stdout

    def test_setup_logging_formatter(self):
        """Test that setup_logging configures the correct formatter."""
        setup_logging(verbose=False)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        assert formatter is not None
        assert isinstance(formatter, logging.Formatter)

        # Test the format by creating a test record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        assert formatted == "INFO: Test message"

    def test_setup_logging_clears_existing_handlers(self):
        """Test that setup_logging clears existing handlers."""
        root_logger = logging.getLogger()

        # Count existing handlers (pytest may have added some)
        initial_count = len(root_logger.handlers)

        # Add some dummy handlers
        dummy_handler1 = logging.StreamHandler()
        dummy_handler2 = logging.StreamHandler()  # Use StreamHandler instead of FileHandler
        root_logger.addHandler(dummy_handler1)
        root_logger.addHandler(dummy_handler2)

        assert len(root_logger.handlers) == initial_count + 2

        # Setup logging should clear them
        setup_logging(verbose=False)

        assert len(root_logger.handlers) == 1
        # The new handler should not be one of the old ones
        assert root_logger.handlers[0] not in [dummy_handler1, dummy_handler2]

        # Clean up the dummy handlers to avoid ResourceWarning
        dummy_handler1.close()
        dummy_handler2.close()

    def test_setup_logging_multiple_calls(self):
        """Test that multiple calls to setup_logging work correctly."""
        # First call
        setup_logging(verbose=False)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) == 1

        # Second call with different settings
        setup_logging(verbose=True)
        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) == 1  # Should still be only one handler

    @patch("logging.StreamHandler")
    def test_setup_logging_handler_configuration(self, mock_stream_handler):
        """Test that setup_logging properly configures the handler."""
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler

        setup_logging(verbose=False)

        # Verify StreamHandler was created with stdout
        mock_stream_handler.assert_called_once_with(sys.stdout)

        # Verify setFormatter was called on the handler
        mock_handler.setFormatter.assert_called_once()

        # Verify formatter is of correct type
        call_args = mock_handler.setFormatter.call_args[0]
        formatter = call_args[0]
        assert isinstance(formatter, logging.Formatter)

    def test_setup_logging_level_mapping(self):
        """Test the level mapping for verbose flag."""
        # Test non-verbose -> INFO
        setup_logging(verbose=False)
        assert logging.getLogger().level == logging.INFO

        # Clean up
        logging.getLogger().handlers.clear()

        # Test verbose -> DEBUG
        setup_logging(verbose=True)
        assert logging.getLogger().level == logging.DEBUG


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_with_name(self):
        """Test get_logger with specific name."""
        logger_name = "test.module"
        logger = get_logger(logger_name)

        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name

    def test_get_logger_without_name(self):
        """Test get_logger with None name."""
        logger = get_logger(None)

        assert isinstance(logger, logging.Logger)
        assert logger.name == "root"

    def test_get_logger_with_empty_string(self):
        """Test get_logger with empty string name."""
        logger = get_logger("")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "root"

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        name = "test.module"
        logger1 = get_logger(name)
        logger2 = get_logger(name)

        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """Test that get_logger returns different instances for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name

    @patch("logging.getLogger")
    def test_get_logger_calls_logging_getlogger(self, mock_getlogger):
        """Test that get_logger properly calls logging.getLogger."""
        mock_logger = Mock()
        mock_getlogger.return_value = mock_logger

        test_name = "test.logger"
        result = get_logger(test_name)

        mock_getlogger.assert_called_once_with(test_name)
        assert result == mock_logger

    def test_get_logger_hierarchical_names(self):
        """Test get_logger with hierarchical logger names."""
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")
        grandchild_logger = get_logger("parent.child.grandchild")

        assert parent_logger.name == "parent"
        assert child_logger.name == "parent.child"
        assert grandchild_logger.name == "parent.child.grandchild"

        # Test hierarchy relationship
        assert child_logger.parent == parent_logger
        assert grandchild_logger.parent == child_logger


class TestLoggingIntegration:
    """Integration tests for logging configuration."""

    def teardown_method(self):
        """Clean up logging configuration after each test."""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)

    def test_setup_and_get_logger_integration(self):
        """Test that setup_logging and get_logger work together."""
        # Capture stdout
        original_stdout = sys.stdout
        captured_output = io.StringIO()

        try:
            sys.stdout = captured_output

            # Setup logging
            setup_logging(verbose=True)

            # Get a logger
            logger = get_logger("test.integration")

            # Logger should use the configured settings
            assert logger.level == logging.NOTSET  # Inherits from root
            assert logging.getLogger().level == logging.DEBUG

            # Test that logging actually works
            logger.info("Test message")

            output = captured_output.getvalue()
            assert "INFO: Test message" in output
        finally:
            sys.stdout = original_stdout

    def test_logging_levels_with_verbose_false(self):
        """Test logging levels when verbose=False."""
        original_stdout = sys.stdout
        captured_output = io.StringIO()

        try:
            sys.stdout = captured_output
            setup_logging(verbose=False)
            logger = get_logger("test.levels")

            # DEBUG should not be logged (level is INFO)
            logger.debug("Debug message")
            debug_output = captured_output.getvalue()
            assert "Debug message" not in debug_output

            # INFO should be logged
            logger.info("Info message")
            info_output = captured_output.getvalue()
            assert "INFO: Info message" in info_output
        finally:
            sys.stdout = original_stdout

    def test_logging_levels_with_verbose_true(self):
        """Test logging levels when verbose=True."""
        original_stdout = sys.stdout
        captured_output = io.StringIO()

        try:
            sys.stdout = captured_output
            setup_logging(verbose=True)
            logger = get_logger("test.levels.verbose")

            # DEBUG should be logged
            logger.debug("Debug message")
            output = captured_output.getvalue()
            assert "DEBUG: Debug message" in output

            # INFO should also be logged
            logger.info("Info message")
            output = captured_output.getvalue()
            assert "INFO: Info message" in output
        finally:
            sys.stdout = original_stdout

    def test_formatter_output_format(self):
        """Test the actual output format of the formatter."""
        original_stdout = sys.stdout
        captured_output = io.StringIO()

        try:
            sys.stdout = captured_output
            setup_logging(verbose=False)
            logger = get_logger("test.format")

            logger.info("Test message")
            logger.warning("Warning message")
            logger.error("Error message")

            output = captured_output.getvalue()

            # Check the format includes level and message
            assert "INFO: Test message" in output
            assert "WARNING: Warning message" in output
            assert "ERROR: Error message" in output
        finally:
            sys.stdout = original_stdout

    def test_multiple_loggers_share_configuration(self):
        """Test that multiple loggers share the same configuration."""
        original_stdout = sys.stdout
        captured_output = io.StringIO()

        try:
            sys.stdout = captured_output
            setup_logging(verbose=True)

            logger1 = get_logger("module1")
            logger2 = get_logger("module2")

            # Both should inherit from root logger
            root_logger = logging.getLogger()
            assert logger1.parent == root_logger
            assert logger2.parent == root_logger

            # Both should use the same handler configuration
            logger1.debug("Message from logger1")
            logger2.debug("Message from logger2")

            output = captured_output.getvalue()
            assert "DEBUG: Message from logger1" in output
            assert "DEBUG: Message from logger2" in output
        finally:
            sys.stdout = original_stdout
