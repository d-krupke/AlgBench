from algbench.benchmark import Benchmark


def test_simple():
    benchmark = Benchmark("./test_benchmark")

    def f(x, _test=2, default="default"):
        print(x)
        return {"r1": x, "r2": "test"}

    benchmark.add(f, 1, _test=None)
    benchmark.add(f, 2)
    benchmark.add(f, 3, _test=None)

    benchmark.compress()

    for entry in benchmark:
        if "environment" in entry["env"]:
            entry["env"].pop("environment")
        print(entry)

    benchmark.delete()
