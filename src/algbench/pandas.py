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
                print(indentation * "|", "...")  # flake8: noqa T201
            return
        if isinstance(val, dict):
            if max_depth == 1:
                print(indentation * "|", f"{key}: ...")  # flake8: noqa T201
            else:
                print(indentation * "|", f"{key}:")  # flake8: noqa T201
                _describe_data(val, indentation + 1, max_length, max_depth - 1)
        else:
            val_text = str(val)
            if len(val_text) > 80:
                val_text = val_text[:77] + "..."
            print(indentation * "|", f"{key}: {val_text}")  # flake8: noqa T201


def describe(path: str):
    """
    Describe the benchmark by printing the first entry.
    """

    print("An entry in the database can look like this:")  # flake8: noqa T201
    print("_____________________________________________")  # flake8: noqa T201
    entry = Benchmark(path).front()
    if not entry:
        return
    _describe_data(entry, 0, 20, 5)
    print("______________________________________________")  # flake8: noqa T201
    print(  # flake8: noqa T201
        "Note that this is only based on the first entry,"
        " other entries could differ."
    )


def read_as_pandas(
    path: str, row_creator: typing.Callable[[typing.Dict], typing.Optional[typing.Dict]]
) -> pd.DataFrame:
    """
    Read the benchmark as pandas table.
    For this, you have to tell the function, which data should
    go into which column. If you want to skip an entry, return None (or an empty dict) in the row_creator.

    An example could look like this:

    .. code-block:: python

        t = read_as_pandas(
            "./03_benchmark_data/",
            lambda result: {
                "instance": result["parameters"]["args"]["instance_name"],
                "strategy": result["parameters"]["args"]["alg_params"]["strategy"],
                "interchange": result["parameters"]["args"]["alg_params"].get(
                    "interchange", None
                ),
                "colors": result["result"]["n_colors"],
                "runtime": result["runtime"],
                "num_vertices": result["result"]["num_vertices"],
                "num_edges": result["result"]["num_edges"],
            },
        )

    :param path: Path to the benchmark
    :param row_creator: Function that creates a row from an entry
    :return: Pandas DataFrame
    """
    data: typing.Dict[str, list] = {}
    n = 0
    benchmark = Benchmark(path)
    for entry in benchmark:
        row = row_creator(entry)
        if not row:
            # Skip entry
            continue
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
