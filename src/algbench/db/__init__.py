"""
This module provides some datastructures to save
JSON-data in an NFS.
"""
# flake8: noqa F401
from .nfs_json_list import NfsJsonList
from .nfs_json_dict import NfsJsonDict
from .nfs_json_set import NfsJsonSet

__all__ = ["NfsJsonList", "NfsJsonDict", "NfsJsonSet"]
