"""
Code for capturing logs and returning them as a list of JSON compatible
dictionaries. You don't need to use this code directly. Use the
``Benchmark.capture_logger`` method instead.
"""

import logging
from typing import Optional

from .db.json_serializer import to_json
from .utils import Timer


class JsonLogHandler(logging.Handler):
    """
    A logging handler that stores log entries in a list of JSON compatible
    dictionaries.
    """

    def __init__(self, level=logging.NOTSET) -> None:
        """
        :param level: The level of the logger to catch.
        """
        super().__init__(level)
        self._log = []
        self._timer = Timer()

    def emit(self, record: logging.LogRecord) -> None:
        data = {}
        data.update(record.__dict__)
        data["runtime"] = self._timer.time()
        self._log.append(to_json(data))

    def reset(self):
        self._timer.reset()
        self._log = []

    def get_entries(self) -> list:
        return self._log


class JsonLogCapture:
    """
    A context manager that captures logs and returns them as a list of JSON
    """

    def __init__(
        self,
        logger_name: str,
        level=logging.NOTSET,
        handler: Optional[JsonLogHandler] = None,
    ) -> None:
        """
        :param logger_name: The name of the logger to catch.
        :param level: The level of the logger to catch.
        """
        self._logger = logging.getLogger(logger_name)
        self._level = level
        self._prior_level = self._logger.getEffectiveLevel()
        self._json_log: JsonLogHandler = handler if handler else JsonLogHandler(level)

    def __enter__(self):
        self._json_log.reset()
        self._logger.addHandler(self._json_log)
        if self._level:
            self._prior_level = self._logger.getEffectiveLevel()
            self._logger.setLevel(self._level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logger.removeHandler(self._json_log)
        self._json_log.close()
        if self._level:
            self._logger.setLevel(self._prior_level)

    def get_entries(self) -> list:
        """
        Returns the log entries as a list of JSON compatible dictionaries.
        """
        return self._json_log.get_entries()
