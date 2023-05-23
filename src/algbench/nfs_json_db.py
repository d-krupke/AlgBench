import os
import pathlib
import typing

import datetime
import json
import logging
import os.path
import random
import socket
import zipfile
from zipfile import ZipFile

from .json_serializer import to_json

_log = logging.getLogger("AlgBench")

class NfsJsonList:
    """
    A simple database to dump data (dictionaries) into. Should be reasonably threadsafe
    even for slurm pools with NFS.
    """

    def __init__(self, path: typing.Union[str, pathlib.Path]):
        self.path = path
        if not os.path.exists(path):
            # Could fail in very few unlucky cases on an NFS (parallel creations)
            os.makedirs(path, exist_ok=True)
            _log.info(f"Created new database '{path}'.")
        if os.path.isfile(path):
            raise RuntimeError(
                f"Cannot create database {path} because there exists an equally named file."
            )
        self._subfile_path = self._get_unique_name()
        self._cache = []

    def _get_unique_name(self, __tries=3):
        """
        Generate a unique file name to prevent collisions of parallel processes.
        """
        if __tries <= 0:
            raise RuntimeError("Could not generate a unique file name. This is odd.")
        hostname = socket.gethostname()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        rand = random.randint(0, 10000)
        name = f"{timestamp}-{hostname}-{rand}.data"
        if os.path.exists(name):
            return self._get_unique_name(__tries=__tries - 1)
        return name

    def compress(self, compression=zipfile.ZIP_LZMA, compresslevel=None):
        """
        Warning: This may not be threadsafe! If you want to extract all data to
        a single file, just use 'read' and dump the output into a single json.
        """
        compr_path = os.path.join(self.path, "_compressed.zip")
        with ZipFile(compr_path, "a", compression=compression,
                     compresslevel=compresslevel) as z:
            for file_name in os.listdir(self.path):
                path = os.path.join(self.path, file_name)
                if not os.path.isfile(path) or not path.endswith(".data"):
                    continue
                if os.path.getsize(path) <= 0:
                    _log.warning(f"Skipping '{path}' due to zero size.")
                    continue
                _log.info(f"Compressing '{file_name}' of size {os.path.getsize(path)}.")
                z.write(path, file_name)
                os.remove(path)
        _log.info(f"Compressed database has size {os.path.getsize(compr_path)}.")

    def extend(self, entries: typing.List, flush=True):
        _log.info(f"Adding {len(entries)} items to database.")
        self._cache += [to_json(e) for  e in entries]
        if flush:
            self.flush()

    def append(self, entry, flush=True):
        self.extend([entry], flush)

    def flush(self):
        if not self._cache:
            return
        path = os.path.join(self.path, self._subfile_path)
        with open(path, "a") as f:
            for data in self._cache:
                data = to_json(data)
                f.write(json.dumps(data) + "\n")
            _log.info(f"Wrote {len(self._cache)} entries to disk.")
        if os.path.getsize(path) <= 0:
            raise RuntimeError("Could not write to disk. Resulting file has zero size.")
        if not os.path.isfile(path):
            raise RuntimeError("Could not write to disk for unknown reasons.")
        self._cache.clear()

    def load(self) -> typing.List:
        data = list(self._cache)
        # load compressed data
        compr_path = os.path.join(self.path, "_compressed.zip")
        if os.path.exists(compr_path):
            with ZipFile(compr_path, "r") as z:
                for filename in z.filelist:
                    with z.open(filename, "r") as f:
                        for line in f.readlines():
                            data.append(json.loads(line))
        # load uncompressed data
        for fp in os.listdir(self.path):
            path = os.path.join(self.path, fp)
            if not os.path.isfile(path) or not path.endswith(".data"):
                continue
            with open(path, "r") as f:
                for entry in f.readlines():
                    try:
                        data.append(json.loads(entry))
                    except:
                        # Just continue. Probably a synchronization thing of the NFS.
                        _log.warning(f"Could not load \"{entry}\" in \"{path}\".")
        return data

    def clear(self):
        """
        Clear database (cache and disk). Note that remaining data in the
        cache of other nodes may still be written.
        """
        # cache
        self._cache.clear()
        # compressed
        compr_path = os.path.join(self.path, "_compressed.zip")
        if os.path.exists(compr_path):
            os.remove(compr_path)
        # remaining .data files
        for fp in os.listdir(self.path):
            path = os.path.join(self.path, fp)
            if not os.path.isfile(path) or not str(path).endswith(".data"):
                continue
            os.remove(path)

    def __del__(self):
        self.flush()

class NfsJsonSet:
    def __init__(self, path) -> None:
        self._db  = NfsJsonList(path)
        self._values = set()
        self.load()
    
    def load(self):
        for row in self._db.load():
            self._values.update(row)

    def __contains__(self, item):
        return  item in  self._values

    def add(self, item):
        if item not in self._values:
            self._db.append([item])
            self._values.add(item)

    def update(self,  items):
        for item  in items:
            self.add(item)

    def __iter__(self):
        for item in self._values:
            yield item
    
    def compress(self):
        """
        WARNING: This operation is not thread-safe!
        """
        self.load()  # in case there have been writes in the meantime
        self._db.clear()
        self._db.extend(list(self._values))
        self._db.compress()

    def clear(self):
        self._db.clear()
        self._values.clear()
        