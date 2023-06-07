import typing

from .json_serializer import to_json
from .nfs_json_list import NfsJsonList


class NfsJsonSet:
    def __init__(self, path) -> None:
        self._db = NfsJsonList(path)
        self._values: typing.Set = set()
        self.load()

    def load(self):
        for row in self._db.load():
            self._values.update(row)

    def __contains__(self, item):
        return item in self._values

    def add(self, item):
        item = to_json(item)
        if item not in self._values:
            self._db.append([item])
            self._values.add(item)
        return item

    def update(self, items):
        for item in items:
            self.add(item)

    def __iter__(self):
        yield from self._values

    def compress(self):
        """
        WARNING: This operation is not thread-safe!
        """
        self.load()  # in case there have been writes in the meantime
        self._db.clear()
        self._db.append(list(self._values))
        self._db.compress()

    def clear(self):
        self._db.clear()
        self._values.clear()

    def delete(self):
        self._db.delete()
