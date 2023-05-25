import shutil
from .fingerprint import fingerprint
from .db import NfsJsonSet, NfsJsonDict, NfsJsonList
from .environment import get_environment_info


import os
import typing


class BenchmarkDb:
    def __init__(self, path) -> None:
        self.path = path
        self._arg_fingerprints = NfsJsonSet(os.path.join(path, "arg_fingerprints"))
        self._arg_data = NfsJsonDict(os.path.join(path, "arg_dict"))
        self._data = NfsJsonList(os.path.join(path, "results"))
        self._env_data = NfsJsonDict(os.path.join(path, "env"))

    def contains_fingerprint(self, fingerprint):
        return fingerprint in self._arg_fingerprints

    def insert(self, entry: typing.Dict):
        # extract data from entry
        env_fingp = entry["data"]["env_fingerprint"]
        env_data = entry["env"]
        arg_fingerprint = entry["data"]["args_fingerprint"]
        arg_data = entry["parameters"]
        result = entry["data"]
        # write into database
        self._arg_fingerprints.add(arg_fingerprint)
        self._arg_data[arg_fingerprint] = arg_data
        self._env_data[env_fingp] = env_data
        self._data.append(result)

    def add(self, arg_fingerprint, arg_data, result):
        self._arg_fingerprints.add(arg_fingerprint)
        self._arg_data[arg_fingerprint] = arg_data
        env_data = get_environment_info()
        env_fingp = fingerprint(env_data)
        self._env_data[env_fingp] = env_data
        result["env_fingerprint"] = env_fingp
        result["args_fingerprint"] = arg_fingerprint
        self._data.append(result)

    def compress(self):
        self._arg_fingerprints.compress()
        self._arg_data.compress()
        self._data.compress()

    def delete(self):
        self._arg_fingerprints.delete()
        self._arg_data.delete()
        self._data.delete()
        self._env_data.delete()
        shutil.rmtree(self.path)

    def clear(self):
        self._arg_fingerprints.clear()
        self._arg_data.clear()
        self._data.clear()
        self._env_data.clear()

    def get_env_info(self, env_fingerprint):
        return self._env_data[env_fingerprint]

    def get_args_info(self, arg_fingerprint):
        return self._arg_data[arg_fingerprint]

    def __iter__(self):
        for entry in self._data:
            env_data = self.get_env_info(entry["env_fingerprint"])
            arg_data = self.get_args_info(entry["args_fingerprint"])
            yield {"parameters": arg_data, "env": env_data, "data": entry}

    def front(self) -> typing.Optional[typing.Dict]:
        try:
            return next(self.__iter__())
        except StopIteration:
            return None
