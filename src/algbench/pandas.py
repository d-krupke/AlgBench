import typing
import pandas as pd
from .benchmark import Benchmark


def _describe_data(
    data: typing.Dict, indentation: int, max_length: int, max_depth: int
):
    if max_depth == 0:
        return
    for i, (key, val) in enumerate(data.items()):
        if i >= max_length:
            if i < len(data) - 1:
                print(indentation * "|", "...")
            return
        if isinstance(val, dict):
            if max_depth == 1:
                print(indentation * "|", f"{key}: ...")
            else:
                print(indentation * "|", f"{key}:")
                _describe_data(val, indentation + 1, max_length, max_depth - 1)
        else:
            val_text = str(val)
            if len(val_text) > 80:
                val_text = val_text[:77] + "..."
            print(indentation * "|", f"{key}: {val_text}")


def describe(path: str):
    """
    Describe the benchmark by printing the first entry.
    """
    entry = Benchmark(path).front()
    if not entry:
        return
    _describe_data(entry, 0, 20, 5)


def read_as_pandas(
    path: str, row_creator: typing.Callable[[typing.Dict], typing.Dict]
) -> pd.DataFrame:
    """
    Read the benchmark as pandas table.
    For this, you have to tell the function, which data should
    go into which row.
    """
    data: typing.Dict[str, list] = {}
    n = 0
    benchmark = Benchmark(path)
    for entry in benchmark:
        row = row_creator(entry)
        for key, value in row.items():
            if key not in data:
                data[key] = n * []
            data[key].append(value)
            n += 1
        # Fill up missing entries with None
        for column in data:
            if column not in row:
                data[column].append(None)
    return pd.DataFrame(data=data)
