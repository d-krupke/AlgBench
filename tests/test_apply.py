import typing

from algbench import Benchmark


def test_apply():
    benchmark = Benchmark("./test_apply")

    def generate_entry(args):
        return {"entry_index": args["index"], "data": f"Data for entry {args['index']}"}

    for i in range(20):
        benchmark.add(generate_entry, {"index": i})

    benchmark.compress()

    def db_count_entries(b: Benchmark) -> int:
        return len([0 for _ in b])

    assert db_count_entries(benchmark) == 20

    def func(entry: typing.Dict):
        if entry["result"]["entry_index"] % 2 == 1:
            return None
        else:
            del entry["timestamp"]
            del entry["runtime"]
            return entry

    benchmark.apply(func)

    assert db_count_entries(benchmark) == 10

    for entry in benchmark:
        assert "timestamp" not in entry
        assert "result" in entry

    benchmark.repair()  # implies both a delete_if() and apply() call
    assert db_count_entries(benchmark) == 10

    benchmark.delete()
