"""Utilities."""

import re
import sys
from datetime import datetime
from typing import ClassVar


class Logger:
    LEVELS: ClassVar[dict[str, int]] = {
        "fatal": 0,
        "error": 1,
        "warn": 2,
        "info": 3,
        "debug": 4,
        "trace": 5,
    }

    def __init__(self, level: str = "info"):
        self.level = self.LEVELS.get(level.lower(), 3)

    def _log(self, level: str, message: str, *args) -> None:
        if self.LEVELS.get(level, 3) > self.level:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = message % args if args else message
        stream = sys.stderr if level in ("fatal", "error") else sys.stdout
        print(f"[{timestamp}] [{level.upper()}] {msg}", flush=True, file=stream)

    def fatal(self, message: str, *args) -> None:
        self._log("fatal", message, *args)
        sys.exit(1)

    def error(self, message: str, *args) -> None:
        self._log("error", message, *args)

    def warn(self, message: str, *args) -> None:
        self._log("warn", message, *args)

    warning = warn

    def info(self, message: str, *args) -> None:
        self._log("info", message, *args)

    def debug(self, message: str, *args) -> None:
        self._log("debug", message, *args)

    def trace(self, message: str, *args) -> None:
        self._log("trace", message, *args)


log = Logger()
logger = log


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def text_content(element):
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()
