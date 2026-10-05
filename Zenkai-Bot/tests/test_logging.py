import json
import logging
import sys

from zenkai.core.logging import JsonFormatter


def make_record(message: str, *, exc_info: object = None) -> logging.LogRecord:
    return logging.LogRecord("test", logging.ERROR, __file__, 1, message, (), exc_info)


def test_json_formatter_redacts_message_values_without_hiding_benign_words() -> None:
    payload = json.loads(
        JsonFormatter().format(make_record("tokenizer and secretary token=secret-value"))
    )

    assert payload["message"] == "tokenizer and secretary token=[REDACTED]"
    assert "secret-value" not in json.dumps(payload)


def test_json_formatter_redacts_exception_values() -> None:
    try:
        raise ValueError("authorization: Bearer secret-value")
    except ValueError:
        payload = json.loads(JsonFormatter().format(make_record("failed", exc_info=sys.exc_info())))
        serialized = json.dumps(payload)

    assert "secret-value" not in serialized
    assert "authorization: [REDACTED]" in payload["exception"]


def test_json_formatter_redacts_url_credentials_and_raw_authorization() -> None:
    payload = json.loads(
        JsonFormatter().format(
            make_record(
                "postgresql://user:db-password@db/name "
                "redis://:redis-password@cache/0 Bearer raw-token"
            )
        )
    )

    assert payload["message"] == (
        "postgresql://[REDACTED]@db/name redis://[REDACTED]@cache/0 Bearer [REDACTED]"
    )
    assert "db-password" not in json.dumps(payload)
    assert "redis-password" not in json.dumps(payload)
    assert "raw-token" not in json.dumps(payload)


def test_json_formatter_redacts_nested_sensitive_values() -> None:
    record = make_record("failed")
    record.context = {
        "profile": {"api_key": "secret-value"},
        "detail": "password=hunter2",
        "raw": b"password=bytes-secret",
    }

    payload = json.loads(JsonFormatter().format(record))

    assert payload["context"] == {
        "profile": {"api_key": "[REDACTED]"},
        "detail": "password=[REDACTED]",
        "raw": "password=[REDACTED]",
    }
    assert "secret-value" not in json.dumps(payload)
    assert "hunter2" not in json.dumps(payload)
