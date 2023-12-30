from algbench import Benchmark


def test_fingerprinting():
    benchmark = Benchmark("./test_fingerprinting")
    benchmark.clear()

    def func(x):
        return {"val": x, "twice_val": 2 * x}

    fp1 = benchmark.fingerprint()

    for x in range(50):
        benchmark.add(func, x)

    fp2 = benchmark.fingerprint()
    assert fp1 != fp2

    for x in range(50):
        benchmark.add(func, x)
    assert fp2 == benchmark.fingerprint()

    benchmark.compress()
    assert fp2 == benchmark.fingerprint()

    for x in range(51):
        benchmark.add(func, x)
    fp3 = benchmark.fingerprint()
    assert fp3 != fp2

    benchmark.compress()
    assert fp3 == benchmark.fingerprint()

    benchmark.repair()
    assert fp3 == benchmark.fingerprint()

    def removeLast(d):
        if d["result"]["val"] >= 50:
            return None
        else:
            return d

    benchmark.apply(removeLast)
    assert fp2 == benchmark.fingerprint()

    benchmark.clear()
    assert fp1 == benchmark.fingerprint()

    benchmark.delete()


if __name__ == "__main__":
    test_fingerprinting()
