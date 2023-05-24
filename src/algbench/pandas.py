import typing
import pandas as pd
from .benchmark import Benchmark
import typing

def describe_data(data: typing.Dict, indention: int, max_length: int, max_depth: int):
    if max_depth == 0:
        return
    for i, (key, val) in enumerate(data.items()):
        if i>=max_length:
            if (i<len(data)-1):
                print(indention*"|", "...")
            return
        if isinstance(val, dict):
            if max_depth==1:
                print(indention*"|", f"{key}: ...")
            else:
                print(indention*"|", f"{key}:")
                describe_data(val, indention+1, max_length, max_depth-1)
        else:
            val_text = str(val)
            if len(val_text)>80:
                val_text = val_text[:77]+"..."
            print(indention*"|", f"{key}: {val_text}")



def describe(path: str):
    entry = Benchmark(path).front()
    if not entry:
        return
    parameters = entry["parameters"]
    print("parameters:")
    describe_data(parameters, 1, 10, 5)
    env = entry["env"]
    print("env:")
    describe_data(env, 1, 5, 3)
    data= entry["data"]
    print("data:")
    describe_data(data, 1, 20, 5)


def read_as_pandas(path: str,
                    row_creator: typing.Callable[[typing.Dict], typing.Dict])\
       -> pd.DataFrame:
    data: typing.Dict[str, list] = {}
    n = 0
    benchmark = Benchmark(path)
    for entry in benchmark:
        for key, value in row_creator(entry).items():
            if key not in data:
                data[key] = n*[]
            data[key].append(value)
            n+=1
        # Fill up missing entries with None
        for column in data:
            if column not in entry:
                data[column].append(None)
    return pd.DataFrame(data=data)