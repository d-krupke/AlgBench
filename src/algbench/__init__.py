"""
AlgBench is designed to perform benchmarks on algorithms.
It saves a lot of the information automatically, reducing
the usual boilerplate code.

.. code-block:: python

    benchmark = Benchmark("./test_benchmark")


    def f(x, _test=2, default="default"):
        print("Run Algorithm!")
        x = x + x
        return {"r1": x, "r2": "test"}


    benchmark.add(f, 1, _test=None)
    benchmark.add(f, 2)
    benchmark.add(f, 3, _test=None)

    benchmark.compress()

    for entry in benchmark:
        print(entry["parameters"], entry["data"])

    benchmark.delete()

"""

# flake8: noqa F401
from .benchmark import Benchmark
from .pandas import read_as_pandas, describe
from .log_capture import JsonLogHandler, JsonLogCapture

# Add __version__ variable from package information.
# https://packaging-guide.openastronomy.org/en/latest/minimal.html#my-package-init-py
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass  # package is not installed

__all__ = [
    "Benchmark",
    "read_as_pandas",
    "describe",
    "JsonLogHandler",
    "JsonLogCapture",
]
