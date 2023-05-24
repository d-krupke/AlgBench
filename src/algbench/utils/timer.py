"""
In many situations we need to measure the time. This timer makes it easy.
"""

import time
import typing


class Timer:
    """
    A simple timer for measuring time.
    """

    def __init__(self, runtime: float = 0.0):
        self.runtime = runtime
        self.start = time.time()
        self.saved_times: typing.List[typing.Tuple[float, str]] = []

    def remaining(self) -> float:
        """
        The remaining time.
        """
        return self.runtime - self.time()

    def time(self) -> float:
        """
        Time since the creation of the timer.
        """
        return time.time() - self.start

    def reset(self, runtime: typing.Optional[float] = None):
        if runtime is not None:
            self.runtime = runtime
        self.start = time.time()
        self.saved_times = []

    def __bool__(self):
        """
        Returns true if there is still time remaining.
        """
        return not self.is_out_of_time()

    def is_out_of_time(self) -> bool:
        return self.remaining() < 0

    def lap(self, label):
        self.saved_times.append((self.time(), label))

    def get_laps(self):
        return list(self.saved_times)

    def check(self):
        if not bool(self):
            raise TimeoutError()
