"""Comprehensive tests for pandas.py to improve coverage."""

import pandas as pd
from algbench import Benchmark, describe, read_as_pandas


def test_describe_empty_benchmark(capsys):
    """Test describe() with an empty benchmark."""
    bench = Benchmark("./test_describe_empty")

    describe("./test_describe_empty")

    captured = capsys.readouterr()
    assert "An entry in the database can look like this:" in captured.out

    bench.delete()


def test_describe_with_data(capsys):
    """Test describe() with actual data."""
    bench = Benchmark("./test_describe_data")

    def dummy_func(x: int, nested: dict) -> dict:
        return {"result": x, "nested_data": nested, "long_string": "a" * 100}

    bench.add(dummy_func, 42, {"level1": {"level2": {"level3": "deep"}}})

    describe("./test_describe_data")

    captured = capsys.readouterr()
    output = captured.out

    # Check basic structure
    assert "An entry in the database can look like this:" in output
    assert "Note that this is only based on the first entry" in output

    # Check that some data is displayed
    assert "result:" in output or "timestamp:" in output

    bench.delete()


def test_describe_max_depth_truncation(capsys):
    """Test _describe_data with max_depth truncation."""
    bench = Benchmark("./test_describe_depth")

    def dummy_func(x: int) -> dict:
        # Create deeply nested structure
        return {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "level6": "very deep"
                            }
                        }
                    }
                }
            }
        }

    bench.add(dummy_func, 1)
    describe("./test_describe_depth")

    captured = capsys.readouterr()
    # With max_depth=5, some nested dicts should show "..."
    # This tests line 20 in pandas.py
    assert "..." in captured.out

    bench.delete()


def test_describe_max_length_truncation(capsys):
    """Test _describe_data with max_length truncation."""
    bench = Benchmark("./test_describe_length")

    def dummy_func() -> dict:
        # Create dict with many keys (more than max_length=20)
        return {f"key_{i}": i for i in range(30)}

    bench.add(dummy_func)
    describe("./test_describe_length")

    captured = capsys.readouterr()
    # Should show "..." when max_length is exceeded (lines 15-17)
    assert "..." in captured.out

    bench.delete()


def test_read_as_pandas_basic():
    """Test basic read_as_pandas functionality."""
    bench = Benchmark("./test_read_pandas_basic")

    def compute(x: int, y: int) -> dict:
        return {"sum": x + y, "product": x * y}

    # Add some data
    bench.add(compute, 1, 2)
    bench.add(compute, 3, 4)
    bench.add(compute, 5, 6)

    # Read as pandas
    df = read_as_pandas(
        "./test_read_pandas_basic",
        lambda entry: {
            "x": entry["parameters"]["args"]["x"],
            "y": entry["parameters"]["args"]["y"],
            "sum": entry["result"]["sum"],
            "product": entry["result"]["product"],
            "runtime": entry["runtime"]
        }
    )

    # Verify DataFrame
    assert len(df) == 3
    assert list(df.columns) == ["x", "y", "sum", "product", "runtime"]
    assert df["sum"].tolist() == [3, 7, 11]
    assert df["product"].tolist() == [2, 12, 30]

    bench.delete()


def test_read_as_pandas_with_skip():
    """Test read_as_pandas with skipping entries (return None)."""
    bench = Benchmark("./test_read_pandas_skip")

    def compute(x: int) -> dict:
        return {"value": x}

    # Add some data
    for i in range(10):
        bench.add(compute, i)

    # Read as pandas, skipping even numbers
    df = read_as_pandas(
        "./test_read_pandas_skip",
        lambda entry: {
            "value": entry["result"]["value"]
        } if entry["result"]["value"] % 2 == 1 else None  # Skip even
    )

    # Should only have odd numbers
    assert len(df) == 5
    assert df["value"].tolist() == [1, 3, 5, 7, 9]

    bench.delete()


def test_read_as_pandas_with_empty_dict_skip():
    """Test read_as_pandas with empty dict skip."""
    bench = Benchmark("./test_read_pandas_empty_skip")

    def compute(x: int) -> dict:
        return {"value": x}

    for i in range(5):
        bench.add(compute, i)

    # Return empty dict for some entries (should skip)
    df = read_as_pandas(
        "./test_read_pandas_empty_skip",
        lambda entry: {
            "value": entry["result"]["value"]
        } if entry["result"]["value"] > 2 else {}  # Return empty dict
    )

    # Should only have values > 2
    assert len(df) == 2
    assert df["value"].tolist() == [3, 4]

    bench.delete()


def test_read_as_pandas_missing_columns():
    """Test read_as_pandas with inconsistent columns across rows."""
    bench = Benchmark("./test_read_pandas_missing")

    def compute(x: int, has_extra: bool) -> dict:
        result = {"value": x}
        if has_extra:
            result["extra"] = x * 2
        return result

    # Add entries with and without 'extra' field
    bench.add(compute, 1, True)
    bench.add(compute, 2, False)  # Missing 'extra'
    bench.add(compute, 3, True)
    bench.add(compute, 4, False)  # Missing 'extra'

    # Read as pandas with variable columns
    df = read_as_pandas(
        "./test_read_pandas_missing",
        lambda entry: {
            "value": entry["result"]["value"],
            "extra": entry["result"].get("extra")  # May be missing
        }
    )

    # Verify DataFrame handles missing data
    assert len(df) == 4
    assert "value" in df.columns
    assert "extra" in df.columns
    assert df["value"].tolist() == [1, 2, 3, 4]
    assert pd.isna(df["extra"].iloc[1])  # Should be NaN for missing
    assert pd.isna(df["extra"].iloc[3])  # Should be NaN for missing

    bench.delete()


def test_read_as_pandas_varying_columns_per_row():
    """Test read_as_pandas where row_creator returns different columns."""
    bench = Benchmark("./test_read_pandas_varying")

    def compute(x: int, include_square: bool) -> dict:
        return {"value": x, "doubled": x * 2, "squared": x ** 2}

    bench.add(compute, 1, True)
    bench.add(compute, 2, False)
    bench.add(compute, 3, True)

    # Row creator conditionally includes 'squared'
    df = read_as_pandas(
        "./test_read_pandas_varying",
        lambda entry: {
            "value": entry["result"]["value"],
            "doubled": entry["result"]["doubled"],
            **({"squared": entry["result"]["squared"]}
               if entry["parameters"]["args"]["include_square"] else {})
        }
    )

    # Check that missing columns are filled with None
    assert len(df) == 3
    assert "value" in df.columns
    assert "doubled" in df.columns
    assert "squared" in df.columns

    # Second row should have None for 'squared'
    assert pd.isna(df["squared"].iloc[1])

    bench.delete()


def test_read_as_pandas_empty_benchmark():
    """Test read_as_pandas with empty benchmark."""
    bench = Benchmark("./test_read_pandas_empty")

    df = read_as_pandas(
        "./test_read_pandas_empty",
        lambda entry: {"x": 1}
    )

    # Should return empty DataFrame
    assert len(df) == 0
    assert isinstance(df, pd.DataFrame)

    bench.delete()


def test_describe_long_string_truncation(capsys):
    """Test that long strings are truncated in describe()."""
    bench = Benchmark("./test_describe_long_string")

    def dummy_func() -> dict:
        # Create a very long string (> 80 chars)
        return {"long_value": "x" * 200}

    bench.add(dummy_func)
    describe("./test_describe_long_string")

    captured = capsys.readouterr()
    # Long string should be truncated with "..." (line 27)
    # The truncation happens at 77 chars, so total with "..." is 80
    lines = captured.out.split("\n")
    # Find the line with long_value
    long_value_lines = [line for line in lines if "long_value" in line]
    assert any("..." in line for line in long_value_lines)

    bench.delete()


if __name__ == "__main__":
    print("Running pandas coverage tests...")

    # Run tests manually
    import sys
    from io import StringIO

    class FakeCapsys:
        def __init__(self):
            self.out = ""

        def readouterr(self):
            import sys
            from types import SimpleNamespace
            result = SimpleNamespace(out=self.out, err="")
            self.out = ""
            return result

    # Capture stdout for describe tests
    import sys
    from io import StringIO

    for test_func in [
        test_describe_empty_benchmark,
        test_describe_with_data,
        test_describe_max_depth_truncation,
        test_describe_max_length_truncation,
        test_describe_long_string_truncation,
    ]:
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            fake_capsys = FakeCapsys()
            fake_capsys.out = sys.stdout.getvalue()
            test_func(fake_capsys)
            print(f"✓ {test_func.__name__}")
        finally:
            sys.stdout = old_stdout

    # Run other tests
    for test_func in [
        test_read_as_pandas_basic,
        test_read_as_pandas_with_skip,
        test_read_as_pandas_with_empty_dict_skip,
        test_read_as_pandas_missing_columns,
        test_read_as_pandas_varying_columns_per_row,
        test_read_as_pandas_empty_benchmark,
    ]:
        test_func()
        print(f"✓ {test_func.__name__}")

    print("\nAll pandas coverage tests passed!")
