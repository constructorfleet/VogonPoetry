import pytest
import logging
import structlog
from types import TracebackType
from vogonpoetry.logging import StructLogger, setup_logging, get_logger

def test_structlogger_info_and_debug(monkeypatch):
    logs = []

    class DummyLogger:
        def info(self, msg, *args, **kwargs):
            logs.append(('info', msg, args, kwargs))
        def debug(self, msg, *args, **kwargs):
            logs.append(('debug', msg, args, kwargs))

    monkeypatch.setattr("vogonpoetry.logging.get_logger", lambda name=None: DummyLogger())
    logger = StructLogger("test")
    logger.info("info message", 1, extra={"foo": "bar"})
    logger.debug("debug message", 2)
    assert logs[0][0] == "info"
    assert logs[0][1] == "info message"
    assert logs[0][3]["foo"] == "bar"
    assert logs[1][0] == "debug"
    assert logs[1][1] == "debug message"

def test_structlogger_error_and_warn(monkeypatch):
    logs = []

    class DummyLogger:
        def error(self, msg, *args, **kwargs):
            logs.append(('error', msg, args, kwargs))
        def warn(self, msg, *args, **kwargs):
            logs.append(('warn', msg, args, kwargs))

    monkeypatch.setattr("vogonpoetry.logging.get_logger", lambda name=None: DummyLogger())
    logger = StructLogger("test")
    logger.error("error message", exc_info=True)
    logger.warn("warn message", stack_info=True)
    assert logs[0][0] == "error"
    assert logs[1][0] == "warn"
    assert logs[0][3]["exc_info"] is True
    assert logs[1][3]["stack_info"] is True

def test_structlogger_warning_and_critical(monkeypatch):
    logs = []

    class DummyLogger:
        def warn(self, msg, *args, **kwargs):
            logs.append(('warn', msg, args, kwargs))
        def critical(self, msg, *args, **kwargs):
            logs.append(('critical', msg, args, kwargs))

    monkeypatch.setattr("vogonpoetry.logging.get_logger", lambda name=None: DummyLogger())
    logger = StructLogger("test")
    logger.warning("warning message")
    logger.critical("critical message")
    assert logs[0][0] == "warn"
    assert logs[1][0] == "critical"

def test_structlogger_trace_and_fatal(monkeypatch):
    logs = []

    class DummyLogger:
        def trace(self, msg, *args, **kwargs):
            logs.append(('trace', msg, args, kwargs))
        def fatal(self, msg, *args, **kwargs):
            logs.append(('fatal', msg, args, kwargs))

    monkeypatch.setattr("vogonpoetry.logging.get_logger", lambda name=None: DummyLogger())
    logger = StructLogger("test")
    logger.trace("trace message")
    logger.fatal("fatal message")
    assert logs[0][0] == "trace"
    assert logs[1][0] == "fatal"

def test_structlogger_log(monkeypatch):
    logs = []

    class DummyLogger:
        def log(self, level, msg, *args, **kwargs):
            logs.append((level, msg, args, kwargs))

    monkeypatch.setattr("vogonpoetry.logging.get_logger", lambda name=None: DummyLogger())
    logger = StructLogger("test")
    logger.log(42, "log message", 123, foo="bar")
    assert logs[0][0] == 42
    assert logs[0][1] == "log message"
    assert logs[0][2][0] == 123
    assert logs[0][3]["foo"] == "bar"

def test_setup_logging_sets_logger_class():
    prev_class = logging.getLoggerClass()
    setup_logging()
    assert logging.getLoggerClass() is StructLogger
    # Restore previous logger class to avoid side effects
    logging.setLoggerClass(prev_class)