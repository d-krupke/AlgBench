from .nfs_json_list import NfsJsonList

from .json_serializer import to_json
import typing


class NfsJsonDict:
    def __init__(self, path) -> None:
        self._db = NfsJsonList(path)
        self._values: typing.Dict = dict()
        self.load()

    def load(self):
        data = self._db.load()
        for d in data:
            if not isinstance(d, dict):
                raise ValueError(
                    "Found data that is not a dict. "
                    "Are you sure this is a NfsJsonDict-database?"
                )
            self._values.update(d)

    def __contains__(self, item):
        return item in self._values

    def __setitem__(self, key, value):
        key = str(key)
        value = to_json(value)
        self._db.append({key: value})
        self._values[key] = value

    def __getitem__(self, key):
        return self._values[key]

    def get(self, *args, **kwargs):
        return self._values.get(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._values.update(*args, **kwargs)

    def items(self):
        for key, value in self._values.items():
            yield key, value

    def compress(self):
        self.load()  # in case there have been writes in the meantime
        self._db.clear()
        self._db.append(self._values)
        self._db.compress()

    def delete(self):
        self._db.delete()
