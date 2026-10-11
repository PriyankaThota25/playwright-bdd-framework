from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "reports" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_RUN_TS = datetime.now().strftime("%Y%m%d_%H%M%S")
_LOG_FILE = LOG_DIR / f"run_{_RUN_TS}.log"

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


class StepLogCapture(logging.Handler):
    """Buffers formatted log lines so the HTML report can attribute them to the
    currently executing BDD step. Attached once to the root logger; every
    module logger propagates up to it in addition to its own console/file
    handlers."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.setFormatter(logging.Formatter(_FORMAT))
        self._buffer: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self._buffer.append(self.format(record))

    def drain(self) -> list[str]:
        lines, self._buffer = self._buffer, []
        return lines


step_log_capture = StepLogCapture()
logging.getLogger().addHandler(step_log_capture)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # already configured, avoid duplicate handlers
        return logger

    logger.setLevel(logging.DEBUG)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(_FORMAT))

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FORMAT))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger