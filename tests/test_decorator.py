"""Test decorator-based experiment API."""

from algbench import Benchmark


def test_decorator_basic():
    """Test basic decorator functionality."""
    call_count = {"value": 0}

    bench = Benchmark("./test_decorator_basic")

    @bench.experiment
    def my_func(x: int) -> dict:
        call_count["value"] += 1
        return {"result": x * 2}

    # First call - should run and record
    result1 = my_func(5)
    assert result1 == {"result": 10}
    # Note: Function is called twice on first run (once in run(), once to return)
    # This is a known limitation of the decorator approach
    assert call_count["value"] == 2
    assert len(bench) == 1

    # Second call with same args - function runs but not recorded again
    result2 = my_func(5)
    assert result2 == {"result": 10}
    assert call_count["value"] == 3  # Function is called again
    assert len(bench) == 1  # But not recorded again

    # Call with different args - should run and record
    result3 = my_func(10)
    assert result3 == {"result": 20}
    assert call_count["value"] == 5  # Called twice (run + return)
    assert len(bench) == 2

    bench.delete()


def test_decorator_with_args():
    """Test decorator with arguments (name, tags)."""
    bench = Benchmark("./test_decorator_with_args")

    @bench.experiment(name="custom_name", tags=["test", "example"])
    def my_func(x: int) -> dict:
        return {"result": x + 1}

    result = my_func(42)
    assert result == {"result": 43}
    assert len(bench) == 1

    bench.delete()


def test_decorator_with_underscore_args():
    """Test decorator with underscore arguments (not tracked)."""
    bench = Benchmark("./test_decorator_underscore")

    @bench.experiment
    def process_data(instance_name: str, param: int, _data: list) -> dict:
        return {"size": len(_data), "param": param}

    # First call
    result1 = process_data("test", 5, _data=[1, 2, 3])
    assert result1 == {"size": 3, "param": 5}
    assert len(bench) == 1

    # Same args (excluding _data) - should not run again
    result2 = process_data("test", 5, _data=[4, 5, 6, 7])  # Different _data
    assert result2 == {"size": 4, "param": 5}
    # Should still be 1 because _data is not tracked
    assert len(bench) == 1

    bench.delete()


if __name__ == "__main__":
    test_decorator_basic()
    test_decorator_with_args()
    test_decorator_with_underscore_args()
    print("All decorator tests passed!")
