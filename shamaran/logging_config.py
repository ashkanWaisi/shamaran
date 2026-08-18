"""Safe rotating application logs with basic secret redaction."""

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path


_SECRET = re.compile(
    r"(?i)(authorization|api[_-]?key|token|password)(\s*[:=]\s*)([^\s,;]+)"
)


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _SECRET.sub(r"\1\2[REDACTED]", str(record.msg))
        record.args = ()
        return True


def configure_logging(level: str = "INFO", log_dir: Path = Path("logs")) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_dir / "shamaran.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    handler.addFilter(RedactingFilter())
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    root = logging.getLogger("shamaran")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False
