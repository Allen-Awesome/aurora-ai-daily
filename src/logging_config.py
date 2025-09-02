import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

_DEFAULT_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)

class SimpleJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json
        payload = {
            "ts": self.formatTime(record, datefmt=None),
            "lvl": record.levelname,
            "logger": record.name,
            "func": record.funcName,
            "line": record.lineno,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def _coerce_bool(val: Optional[str], default: bool = False) -> bool:
    if val is None:
        return default
    return str(val).lower() in ("1", "true", "yes", "y", "on")

def setup_logging():
    """Configure project-wide logging once. Safe to call multiple times."""
    if getattr(setup_logging, "_configured", False):
        return

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    json_mode = _coerce_bool(os.getenv("LOG_JSON"), False)
    log_file = os.getenv("LOG_FILE", "news_system.log")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", "1048576"))  # 1MB
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = SimpleJsonFormatter() if json_mode else logging.Formatter(_DEFAULT_FORMAT)

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Rotating file
    fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    setup_logging._configured = True  # type: ignore[attr-defined]


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
