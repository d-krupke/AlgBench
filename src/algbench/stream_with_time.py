



from typing import Iterable, List, Tuple
import io
from .utils import Timer

class StreamWithTime(io.StringIO):
    """
    A StringIO that stores the time of each line.
    """
    def __init__(self) -> None:
        super().__init__()
        self._timer = Timer()
        self._data = []

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
