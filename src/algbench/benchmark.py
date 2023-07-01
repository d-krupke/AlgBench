import datetime
import inspect
import io
import logging
import traceback
import typing
from contextlib import ExitStack, redirect_stderr, redirect_stdout

import yaml

from .benchmark_db import BenchmarkDb
from .db.json_serializer import to_json
from .fingerprint import fingerprint
from .log_capture import JsonLogCapture, JsonLogHandler
from .stream_with_time import StreamWithTime
from .utils import Timer


class Benchmark:
    """
    This is the heart of the library. It allows to run, save, and load
    a benchmark.

    The function `add` will run a configuration, if it is not
    already in the database. You can also split this into `check` and
    `run`. This may be advised if you want to distribute the execution.

    The following functions are thread-safe:
    - exists
    - run
    - add
    - insert
    - front
    - capture_logger
    - unlink_logger
    - __iter__

    Don't call any of the other functions while the benchmark is
    running. It could lead to data loss.
    """

    def __init__(self, path: str, save_output_with_time: bool = True) -> None:
        """
        Just specify the path of where to put the
        database and everything else happens magically.
        Make sure not to use the same path for different
        databases, as they will get mixed.

        :param path: The path to the database.
        :param save_output_with_time: If true, all output (stdout and stderr)
            will be saved with the time it was written. This gives you more
            insights on the runtime of the algorithm, but also increases the
            size of the database.
        """
        self._db = BenchmarkDb(path)
        self._save_output_with_time = save_output_with_time
        self._log_captures = {}

    def capture_logger(self, logger_name: str, level=logging.NOTSET):
        """
        Capture the logs of a logger of the Python logging module.
        This allows you to precisely control which logs you want to
        capture. Prefer logging to stdout/stderr, as just using ``print``
        will not allow you to control the output of sub-algorithms.
        The logging module also allows you to serch more easily for
        specific log entries, if used correctly. However, it is
        more expensive than just using ``print`` as more metadata
        is created. Don't overuse it but only log important events
        in the algorithm.

        :param logger_name: The name of the logger to capture.
        :param level: The level of the logger to capture. The logger will
            will automatically be set to this level while capturing, but
            will be reset afterwards. NOTSET will not change the level.
        :return: None
        """
        self._log_captures[logger_name] = level

    def unlink_logger(self, logger_name: str):
        """
        Stop capturing the logs of a logger of the Python logging module
        while the benchmark is running.
        """
        del self._log_captures[logger_name]

    def _get_arg_data(self, func, args, kwargs):
        sig = inspect.signature(func)
        func_args = {
            k: v.default
            for k, v in sig.parameters.items()
            if v.default is not inspect.Parameter.empty
        }
        func_args.update(sig.bind(*args, **kwargs).arguments)
        data = {
            "func": func.__name__,
            "args": {
                key: value
                for key, value in func_args.items()
                if not key.startswith("_")
            },
        }

        return fingerprint(data), to_json(data)

    def exists(self, func: typing.Callable, *args, **kwargs) -> bool:
        """
        Use this function to check if an entry already exist and thus
        does not have to be run again. If you want to have multiple
        samples, add a sample index argument.

        Caveat: This function may have false negatives. i.e., says that it
        does not exist despite it existing (only for fresh data).
        """
        fingp, _ = self._get_arg_data(func, args, kwargs)
        return self._db.contains_fingerprint(fingp)

    def _get_stream_obj(self):
        if self._save_output_with_time:
            # SteamWithTime is a wrapper around StringIO.
            # It stores the time of each line.
            # getvalue() returns a list of tuples (time, line).
            return StreamWithTime()
        else:
            return io.StringIO()

    def run(self, func: typing.Callable, *args, **kwargs):
        """
        Will add the function call with the arguments
        to the benchmark.

        The output of stdout and stderr will be captured and stored,
        but not printed to the console.
        """
        fingp, arg_data = self._get_arg_data(func, args, kwargs)
        try:
            stdout = self._get_stream_obj()
            stderr = self._get_stream_obj()
            with ExitStack() as logging_stack:
                log_handler = JsonLogHandler()
                for logger_name, level in self._log_captures.items():
                    logging_stack.enter_context(
                        JsonLogCapture(logger_name, level, log_handler)
                    )
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    timestamp = datetime.datetime.now().isoformat()
                    timer = Timer()
                    result = func(*args, **kwargs)
                    runtime = timer.time()
                    self._db.add(
                        arg_fingerprint=fingp,
                        arg_data=arg_data,
                        result={
                            "result": result,
                            "timestamp": timestamp,
                            "runtime": runtime,
                            "stdout": stdout.getvalue(),
                            "stderr": stderr.getvalue(),
                            "logging": log_handler.get_entries(),
                        },
                    )
            print(".", end="")
        except Exception as e:
            print()
            print("Exception while running benchmark.")
            print("=====================================")
            print(yaml.dump(arg_data))
            print("-------------------------------------")
            print("ERROR:", e, f"({type(e)})")
            print(traceback.format_exc())
            print("-------------------------------------")
            raise

    def add(self, func: typing.Callable, *args, **kwargs):
        """
        Will add the function call with the arguments
        to the benchmark if not yet contained.

        Combination of `check` and `run`.
        Will only call `run` if the arguments are not
        yet in the benchmark.
        """
        if not self.exists(func, *args, **kwargs):
            self.run(func, *args, **kwargs)

    def insert(self, entry: typing.Dict):
        """
        Insert a raw entry, as returned by `__iter__` or `front`.
        """
        self._db.insert(entry)

    def compress(self):
        """
        Compress the data of the benchmark to take less disk space.

        NOT THREAD-SAFE!
        """
        self._db.compress()

    def repair(self):
        """
        Repairs the benchmark in case it has some broken entries.

        NOT THREAD-SAFE!
        """
        self.delete_if(lambda data: False)

    def __iter__(self) -> typing.Generator[typing.Dict, None, None]:
        """
        Iterate over all entries in the benchmark.
        Use `front` to get a preview on how an entry looks like.
        """
        for entry in self._db:
            yield entry.copy()

    def delete(self):
        """
        Delete the benchmark and all its files. Do not use it afterwards,
        there are no files left to write results into.
        If you just want to delete the content, use `clear.

        NOT THREAD-SAFE!
        """
        self._db.delete()

    def front(self) -> typing.Optional[typing.Dict]:
        """
        Return the first entry of the benchmark.
        Useful for checking its content.
        """
        return self._db.front()

    def clear(self):
        """
        Clears all entries of the benchmark, without deleting
        the benchmark itself. You can continue to use it afterwards.

        NOT THREAD-SAFE!
        """
        self._db.clear()

    def delete_if(self, condition: typing.Callable[[typing.Dict], bool]):
        """
        Delete entries if a specific condition is met.
        This is currently inefficiently, as always a copy
        of the benchmark is created.
        Use `front` to get a preview on how an entry that is
        passed to the condition looks like.

        NOT THREAD-SAFE!
        """
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdirname:
            benchmark_copy = Benchmark(tmpdirname)
            for entry in self:
                if not condition(entry):
                    benchmark_copy.insert(entry)
            self.clear()
            for entry in benchmark_copy:
                self.insert(entry)
            self.compress()
            benchmark_copy.delete()
