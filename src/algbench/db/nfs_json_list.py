import datetime
import json
import logging
import os
import os.path
import pathlib
import random
import shutil
import socket
import typing
import zipfile
from zipfile import ZipFile, BadZipFile

from .json_serializer import to_json

_log = logging.getLogger("AlgBench")


class NfsJsonList:
    """
    A simple database to dump data (dictionaries) into. Should be reasonably threadsafe
    even for slurm pools with NFS.
    """

    def __init__(self, path: typing.Union[str, pathlib.Path]):
        self.path: typing.Union[str, pathlib.Path] = path
        if not os.path.exists(path):
            # Could fail in very few unlucky cases on an NFS (parallel creations)
            os.makedirs(path, exist_ok=True)
            _log.info(f"Created new database '{path}'.")
        if os.path.isfile(path):
            msg = f"Cannot create database {path} because there exists an equally named file."
            raise RuntimeError(msg)
        self._subfile_path: typing.Union[str, pathlib.Path] = self._get_unique_name()
        self._cache: typing.List = []

    def _get_unique_name(self, _tries=3):
        """
        Generate a unique file name to prevent collisions of parallel processes.
        """
        if _tries <= 0:
            msg = "Could not generate a unique file name. This is odd."
            raise RuntimeError(msg)
        hostname = socket.gethostname()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        rand = random.randint(0, 10000)
        name = f"{timestamp}-{hostname}-{rand}.data"
        if os.path.exists(name):
            return self._get_unique_name(_tries=_tries - 1)
        return name

    def compress(self, compression=zipfile.ZIP_LZMA, compresslevel=None):
        """
        Warning: This may not be threadsafe! If you want to extract all data to
        a single file, just use 'read' and dump the output into a single json.
        """
        compr_path = os.path.join(self.path, "_compressed.zip")
        with ZipFile(
            compr_path, "a", compression=compression, compresslevel=compresslevel
        ) as z:
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
        serialized_data = [to_json(e) for e in entries]
        self._cache += serialized_data
        if flush:
            self.flush()
        return serialized_data

    def append(self, entry, flush=True):
        return self.extend([entry], flush)[0]

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
            msg = "Could not write to disk. Resulting file has zero size."
            raise RuntimeError(msg)
        if not os.path.isfile(path):
            msg = "Could not write to disk for unknown reasons."
            raise RuntimeError(msg)
        self._cache.clear()

    def iter_cache(self):
        yield from self._cache

    def iter_compressed(self):
        """
        Iterate over all entries in the compressed database.
        This may not represent the whole database if the database is not completely compressed.
        Use the ``__iter__`` method to iterate over the whole database.
        """
        compr_path = os.path.join(self.path, "_compressed.zip")
        if os.path.exists(compr_path):
            with ZipFile(compr_path, "r") as z:
                for filename in z.filelist:
                    yield from self._iter_compressed_file(z, filename, compr_path)

    def _iter_compressed_file(self, zip_file, filename, compr_path):
        try:
            with zip_file.open(filename, "r") as f:
                for line in f.readlines():
                    try:
                        entry = json.loads(line)
                        yield entry
                    except Exception:
                        # Just continue. Probably a synchronization
                        #  thing of the NFS.
                        _log.warning(f'Could not load "{line}" in "{compr_path}".')
        except BadZipFile as e:
            _log.warning(f"Could not open file {filename}. Bad Zip: {e}")

    def iter_uncompressed(self):
        # load uncompressed data
        for fp in os.listdir(self.path):
            path = os.path.join(self.path, fp)
            if not os.path.isfile(path) or not path.endswith(".data"):
                continue
            with open(path) as f:
                for entry in f.readlines():
                    try:
                        entry_ = json.loads(entry)
                        yield entry_
                    except Exception:
                        # Just continue. Probably a synchronization thing of the NFS.
                        _log.warning(f'Could not load "{entry}" in "{path}".')

    def __iter__(self):
        for entry in self.iter_compressed():
            yield entry
        for entry in self.iter_uncompressed():
            yield entry
        for entry in self.iter_cache():
            yield entry

    def load(self) -> typing.List:
        return list(self)

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

    def delete(self):
        self._cache.clear()
        shutil.rmtree(self.path)
