import json
import typing

from .json_serializer import to_json
from .nfs_json_list import NfsJsonList


def _equal(a, b):
    return json.dumps(a) == json.dumps(b)


class NfsJsonDict:
    def __init__(self, path) -> None:
        self._db = NfsJsonList(path)
        self._values: typing.Dict = {}
        self.load()

    def load(self):
        data = self._db.load()
        for d in data:
            if not isinstance(d, dict):
                msg = "Found data that is not a dict. Are you sure this is a NfsJsonDict-database?"
                raise ValueError(msg)
            self._values.update(d)

    def __contains__(self, item: str):
        return item in self._values

    def __setitem__(self, key: str, value):
        key = str(key)
        value = to_json(value)
        if key in self._values and _equal(self._values[key], value):
            return
        self._db.append({key: value})
        self._values[key] = value

    def __getitem__(self, key: str):
        return self._values[key]

    def get(self, *args, **kwargs):
        return self._values.get(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._values.update(*args, **kwargs)

    def items(self):
        yield from self._values.items()

    def compress(self):
        self.load()  # in case there have been writes in the meantime
        self._db.clear()
        self._db.append(self._values)
        self._db.compress()

    def clear(self):
        self._db.clear()
        self._values.clear()

    def delete(self):
        self._db.delete()
