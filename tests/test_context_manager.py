"""Test context manager functionality."""

import os
from algbench import Benchmark


def test_context_manager_basic():
    """Test that Benchmark works as a context manager."""

    def dummy_func(x: int) -> dict:
        return {"result": x * 2}

    # Use as context manager
    with Benchmark("./test_context_mgr") as bench:
        bench.add(dummy_func, 1)
        bench.add(dummy_func, 2)
        bench.add(dummy_func, 3)
        assert len(bench) == 3

    # Verify data persists after context exit
    bench2 = Benchmark("./test_context_mgr")
    assert len(bench2) == 3

    # Cleanup
    bench2.delete()


def test_context_manager_auto_compress():
    """Test that auto_compress works with context manager."""

    def dummy_func(x: int) -> dict:
        return {"result": x * 2}

    # Use with auto_compress
    with Benchmark("./test_auto_compress", auto_compress=True) as bench:
        for i in range(10):
            bench.add(dummy_func, i)

    # Check that compressed file exists
    compressed_path = os.path.join("./test_auto_compress", "results", "_compressed.zip")
    assert os.path.exists(compressed_path), "Compressed file should exist after auto_compress"

    # Verify data is still accessible
    bench2 = Benchmark("./test_auto_compress")
    assert len(bench2) == 10

    # Cleanup
    bench2.delete()


def test_repr_and_str():
    """Test __repr__ and __str__ methods."""

    def dummy_func(x: int) -> dict:
        return {"result": x}

    bench = Benchmark("./test_repr")
    bench.add(dummy_func, 42)

    # Test __repr__
    repr_str = repr(bench)
    assert "Benchmark" in repr_str
    assert "test_repr" in repr_str
    assert "entries=1" in repr_str

    # Test __str__
    str_str = str(bench)
    assert "Benchmark" in str_str
    assert "test_repr" in str_str
    assert "1 entries" in str_str

    # Cleanup
    bench.delete()


if __name__ == "__main__":
    test_context_manager_basic()
    test_context_manager_auto_compress()
    test_repr_and_str()
    print("All context manager tests passed!")
