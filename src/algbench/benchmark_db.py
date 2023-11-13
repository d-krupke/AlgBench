import datetime
import json
import os
import random
import shutil
import sys
import typing

from .db import NfsJsonDict, NfsJsonList, NfsJsonSet
from .environment import get_environment_info
from .fingerprint import fingerprint


class BenchmarkDb:
    def __init__(self, path) -> None:
        self.path = path
        self._create_or_check_info_file()
        self._arg_fingerprints = NfsJsonSet(os.path.join(path, "arg_fingerprints"))
        self._data = NfsJsonList(os.path.join(path, "results"))
        self._env_data = NfsJsonDict(os.path.join(path, "env_info"))

    def _create_or_check_info_file(self):
        info_path = os.path.join(self.path, "algbench.json")
        if os.path.exists(info_path):
            with open(info_path) as f:
                info = json.load(f)
                if info.get("version", "v0.0.0")[1] == "0":
                    msg = "Incompatible database of old version of AlgBench."
                    raise RuntimeError(msg)
        else:
            os.makedirs(self.path, exist_ok=True)
            with open(info_path, "w") as f:
                json.dump({"version": "v1.0.0"}, f)

    def contains_fingerprint(self, fingerprint: str) -> bool:
        return fingerprint in self._arg_fingerprints

    def insert(self, entry: typing.Dict):
        # extract data from entry
        env_fingp = entry["env_fingerprint"]
        env_data = entry["env"]
        arg_fingerprint = entry["args_fingerprint"]
        result = {k: v for k, v in entry.items() if k != "env"}
        # write into database
        self._arg_fingerprints.add(arg_fingerprint)
        self._env_data[env_fingp] = env_data
        self._data.append(result)

    def add(self, arg_fingerprint, arg_data, result):
        argv = (" ".join(sys.argv) if sys.argv else "",)
        self._arg_fingerprints.add(arg_fingerprint)
        env_data = get_environment_info()
        env_fingp = fingerprint(env_data)
        self._env_data[env_fingp] = env_data
        result["env_fingerprint"] = env_fingp
        result["args_fingerprint"] = arg_fingerprint
        result["parameters"] = arg_data
        result["argv"] = argv
        self._data.append(result)

    def compress(self):
        self._arg_fingerprints.compress()
        self._data.compress()
        self._env_data.compress()

    def delete(self):
        self._arg_fingerprints.delete()
        self._data.delete()
        self._env_data.delete()
        shutil.rmtree(self.path)

    def clear(self):
        self._arg_fingerprints.clear()
        self._data.clear()
        self._env_data.clear()

    def get_env_info(self, env_fingerprint, env_data: typing.Optional[NfsJsonDict]=None):
        if not env_data:
            env_data = self._env_data
        return env_data[env_fingerprint]

    def _create_entry_with_env(self, entry: typing.Dict, env_data: typing.Optional[NfsJsonDict]=None):
        entry = entry.copy()
        try:
            if not env_data:
                env_data = self._env_data
            entry["env"] = self.get_env_info(entry["env_fingerprint"], env_data)
            return entry
        except KeyError:
            return None
        
    def __iter__(self):
        for entry in self._data:
            entry_with_env = self._create_entry_with_env(entry)
            if entry_with_env:
                yield entry_with_env

    def front(self) -> typing.Optional[typing.Dict]:
        try:
            return next(self.__iter__())
        except StopIteration:
            return None

    def apply(self, func: typing.Callable[[typing.Dict], typing.Optional[typing.Dict]]):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        rand = random.randint(0, 9999)
        unique_suffix = f"{timestamp}_{rand}"

        old_env_data = self._env_data
        old_env_data.move_directory(os.path.join(self.path, f"env_info{unique_suffix}"))
        old_data = self._data
        old_data.move_directory(os.path.join(self.path, f"results_old{unique_suffix}"))

        self._data = NfsJsonList(os.path.join(self.path, "results"))
        self._env_data = NfsJsonDict(os.path.join(self.path, "env_info"))
        self._arg_fingerprints.clear()

        for entry in old_data:
            new_entry = func(self._create_entry_with_env(entry, env_data=old_env_data))
            if new_entry:
                self.insert(new_entry)

        old_data.delete()
        old_env_data.delete()

    def __len__(self):
        return len(self._arg_fingerprints)
    