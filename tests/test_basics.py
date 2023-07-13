import logging

from algbench import Benchmark, describe


def test_simple():
    benchmark = Benchmark("./test_benchmark")

    def f(x, _test=2, default="default"):
        print(x)
        logging.getLogger("test").info("f(%d)", x)
        return {"r1": x, "r2": "test"}

    benchmark.capture_logger("test", logging.INFO)
    benchmark.add(f, 1, _test=None)
    benchmark.add(f, 2)
    benchmark.add(f, 3, _test=None)

    benchmark.compress()
    benchmark.delete_if(lambda entry: False)
    n = 0
    for entry in benchmark:
        print({k: v for k, v in entry.items() if k != "env"})
        n += 1
    assert n == 3

    describe("./test_benchmark")
    benchmark.delete()
