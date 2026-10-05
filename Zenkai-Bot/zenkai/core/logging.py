import json
import logging
import re
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    sensitive_pattern = re.compile(r"(token|secret|password|api[_-]?key|authorization)", re.I)
    sensitive_text_pattern = re.compile(
        r"""(?ix)
        (?P<prefix>
            ["']?
            (?:token|secret|password|api[_-]?key|authorization)
            ["']?
            \s*[:=]\s*
        )
        (?:(?:bearer|basic)\s+)?
        (?P<value>"[^"\r\n]*"|'[^'\r\n]*'|[^\s,;}\]]+)
        """
    )
    url_credentials_pattern = re.compile(
        r"(?i)(?P<prefix>\b[a-z][a-z0-9+.-]*://)[^/\s:@]*:[^@/\s]+@"
    )
    authorization_value_pattern = re.compile(r"(?i)(?P<scheme>\b(?:bearer|basic))\s+[^\s,;}\]]+")
    reserved_fields = frozenset(
        {
            "args",
            "asctime",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }
    )

    def _redact_text(self, value: str) -> str:
        value = self.sensitive_text_pattern.sub(
            lambda match: f"{match.group('prefix')}[REDACTED]",
            value,
        )
        value = self.url_credentials_pattern.sub(
            lambda match: f"{match.group('prefix')}[REDACTED]@",
            value,
        )
        return self.authorization_value_pattern.sub(
            lambda match: f"{match.group('scheme')} [REDACTED]",
            value,
        )

    def _redact_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: "[REDACTED]"
                if isinstance(key, str) and self.sensitive_pattern.search(key)
                else self._redact_value(item)
                for key, item in value.items()
            }
        if isinstance(value, (list, tuple, set)):
            return [self._redact_value(item) for item in value]
        if isinstance(value, bytes):
            return self._redact_text(value.decode("utf-8", errors="replace"))
        if isinstance(value, str):
            return self._redact_text(value)
        return value

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self._redact_text(record.getMessage()),
        }
        if record.exc_info:
            payload["exception"] = self._redact_text(self.formatException(record.exc_info))
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in self.reserved_fields:
                continue
            payload[key] = self._redact_value(value)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(numeric_level)
    for logger_name in ("discord", "discord.http", "apscheduler", "sqlalchemy.engine"):
        logging.getLogger(logger_name).setLevel(max(numeric_level, logging.WARNING))
