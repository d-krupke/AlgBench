"""
This files are wrapper for the output streams.
They are used to capture the output of the functions
and store it in the database.
"""


import io
from typing import List, Tuple

from .utils import Timer


class PrintingStringIO(io.StringIO):
    """
    A StringIO that additionally prints to a stream.
    """

    def __init__(self, printing_stream=None) -> None:
        super().__init__()
        self._printing_stream = printing_stream

    def _print(self, __s: str) -> None:
        if self._printing_stream:
            self._printing_stream.write(__s)

    def write(self, __s: str) -> int:
        self._print(__s)
        return super().write(__s)


class StreamWithTime(PrintingStringIO):
    """
    A StringIO that stores the time of each line.
    """

    def __init__(self, forward_stream=None) -> None:
        super().__init__(forward_stream)
        self._timer = Timer()
        self._data = []
        self.forward_stream = forward_stream

    def reset(self):
        self._timer.reset()
        self._data = []
        self.truncate(0)
        self.seek(0)

    def _save(self):
        val = super().getvalue()
        if not val:
            return
        self._data.append((self._timer.time(), val))
        self.truncate(0)
        self.seek(0)

    def write(self, __s: str) -> int:
        ret = super().write(__s)
        if "\n" in __s:
            self._save()
        return ret

    def getvalue(self) -> List[Tuple[float, str]]:
        self._save()
        return self._data


class NotSavingIO(PrintingStringIO):
    """
    A StringIO that does not save anything.
    """

    def write(self, __s: str) -> int:
        self._print(__s)
        return len(__s)

    def getvalue(self):
        return None
