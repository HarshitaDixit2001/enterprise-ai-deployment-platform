import json
import logging

from app.core.logging_config import StructuredJsonFormatter, request_id_context


def test_structured_formatter_includes_request_id():
    token = request_id_context.set("req-test-123")

    try:
        record = logging.LogRecord(
            name="app.request",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="request_completed",
            args=(),
            exc_info=None,
        )

        formatted = StructuredJsonFormatter().format(record)
        payload = json.loads(formatted)

        assert payload["message"] == "request_completed"
        assert payload["request_id"] == "req-test-123"
        assert payload["level"] == "INFO"
        assert "timestamp" in payload
    finally:
        request_id_context.reset(token)


def test_explicit_record_request_id_takes_precedence():
    token = request_id_context.set("context-request-id")

    try:
        record = logging.LogRecord(
            name="app.request",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="request_completed",
            args=(),
            exc_info=None,
        )
        record.request_id = "explicit-request-id"

        payload = json.loads(StructuredJsonFormatter().format(record))

        assert payload["request_id"] == "explicit-request-id"
    finally:
        request_id_context.reset(token)


def test_structured_formatter_includes_exception_details():
    try:
        raise ValueError("example failure")
    except ValueError:
        import sys
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="app.test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=10,
        msg="operation_failed",
        args=(),
        exc_info=exc_info,
    )

    payload = json.loads(StructuredJsonFormatter().format(record))

    assert payload["message"] == "operation_failed"
    assert "ValueError: example failure" in payload["exception"]