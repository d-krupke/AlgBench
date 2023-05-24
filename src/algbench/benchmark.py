from contextlib import redirect_stderr, redirect_stdout
import datetime
import io
import inspect
import traceback
import yaml
import typing

from .benchmark_db import BenchmarkDb
from .utils import Timer
from .fingerprint import fingerprint
from .db.json_serializer import to_json


class Benchmark:
    def __init__(self, path) -> None:
        self._db = BenchmarkDb(path)
    
    def _get_arg_data(self, func, args, kwargs):
        sig = inspect.signature(func)
        func_args = sig.bind(*args, **kwargs).arguments
        data = {"func": func.__name__,
                "args": {key: value for key, value in func_args.items()
                 if not key.startswith("_")}}
        
        return fingerprint(data), to_json(data)

    def exists(self, func, *args, **kwargs) -> bool:
        """
        Use this function to check if an entry already exist and thus
        does not have to be run again. If you want to have multiple 
        samples, add a sample index argument.
        Caveat: This function may have false negatives. i.e., says that it
          does not exist despite it existing (only for fresh data).
        """
        fingp, _ = self._get_arg_data(func, args, kwargs)
        return self._db.contains_fingerprint(fingp)
    
    def run(self, func, *args, **kwargs):
        fingp, arg_data = self._get_arg_data(func, args, kwargs)
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    timestamp = datetime.datetime.now().isoformat()
                    timer  = Timer()
                    result = func(*args, **kwargs)
                    runtime = timer.time()
            self._db.add(arg_fingerprint=fingp,
                          arg_data=arg_data,
                            result={"result": result, 
                                 
                                 "timestamp": timestamp,
                                 "runtime": runtime,
                                 "stdout": stdout.getvalue(),
                                 "stderr": stderr.getvalue()})
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

    def add(self, func, *args, **kwargs):
        if not self.exists(func, *args, **kwargs):
            self.run(func, *args, **kwargs)

    def compress(self):
        self._db.compress()

    def repair(self):
        raise NotImplementedError()
    
    def __iter__(self) -> typing.Iterable[typing.Dict]:
        for entry in self._db:
            yield entry.copy()
    
    def delete(self):
        self._db.delete()


