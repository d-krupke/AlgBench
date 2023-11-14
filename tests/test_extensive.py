from algbench import Benchmark


def test_extensive_use_case():
    benchmark = Benchmark("./extensive_benchmark")
    benchmark.clear()
    assert benchmark.empty()

    def f(x, _test=2, default="default"):
        print(x)
        return {"r1": x, "r2": "test"}
    
    for x in range(500):
        benchmark.add(f, x, _test=None)

    assert len(benchmark) == 500
    for x, entry in enumerate(benchmark):
        assert entry["result"]["r1"] == x
    benchmark.compress()
    assert len(benchmark) == 500
    benchmark.delete_if(lambda entry: False)
    assert len(benchmark) == 500
    benchmark_ = Benchmark("./extensive_benchmark")
    assert len(benchmark_) == 500
    benchmark_.compress()
    assert len(benchmark_) == 500
    benchmark_.delete_if(lambda entry: entry["result"]["r1"] % 2 == 0)
    assert len(benchmark_) == 250
    for x, entry in enumerate(benchmark_):
        assert entry["result"]["r1"] == x * 2 + 1
    benchmark_.compress()
    assert len(benchmark_) == 250
    benchmark.delete()

if __name__ == "__main__":
    test_extensive_use_case()