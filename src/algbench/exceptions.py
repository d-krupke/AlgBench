"""
Custom exception classes for AlgBench with helpful error messages.
"""

from pathlib import Path
from typing import Optional


class AlgBenchError(Exception):
    """Base exception for all AlgBench errors."""


class DatabaseError(AlgBenchError):
    """Base class for database-related errors."""


class DatabaseExistsError(DatabaseError):
    """Raised when database path conflicts with an existing file."""

    def __init__(self, path: Path | str) -> None:
        path = Path(path)
        super().__init__(
            f"Cannot create database at '{path}' - a file with this name already exists.\n"
            f"\n"
            f"Suggestions:\n"
            f"  1. Use a different path: Benchmark('./other_path')\n"
            f"  2. Delete the conflicting file: rm '{path}'\n"
            f"  3. If this is an existing benchmark, the path should point to a directory"
        )


class IncompatibleVersionError(DatabaseError):
    """Raised when trying to open a database from an incompatible version."""

    def __init__(self, version: str, path: Path | str) -> None:
        super().__init__(
            f"Incompatible database version '{version}' at '{path}'.\n"
            f"\n"
            f"This database was created with an older version of AlgBench.\n"
            f"Unfortunately, databases from version 0.x are not compatible with version 1.x+.\n"
            f"\n"
            f"Options:\n"
            f"  1. Recreate the benchmark with the current version\n"
            f"  2. Install the older version: pip install algbench=={version[:3]}"
        )


class CorruptedDatabaseError(DatabaseError):
    """Raised when database files are corrupted."""

    def __init__(self, path: Path | str, details: Optional[str] = None) -> None:
        msg = f"Database at '{path}' appears to be corrupted."
        if details:
            msg += f"\n\nDetails: {details}"
        msg += (
            f"\n\nSuggestions:\n"
            f"  1. Try repairing: benchmark.repair()\n"
            f"  2. Check disk space and file permissions\n"
            f"  3. Restore from backup if available"
        )
        super().__init__(msg)


class EmptyDatabaseError(DatabaseError):
    """Raised when trying to access data from an empty database."""

    def __init__(self, path: Path | str) -> None:
        super().__init__(
            f"Database at '{path}' is empty.\n"
            f"\n"
            f"Use benchmark.add() to add entries before querying."
        )


class FingerprintCollisionError(AlgBenchError):
    """Raised when a hash collision is detected (extremely rare)."""

    def __init__(self, fingerprint: str) -> None:
        super().__init__(
            f"Hash collision detected for fingerprint '{fingerprint[:16]}...'.\n"
            f"\n"
            f"This is extremely rare. Please report this as a bug.\n"
            f"As a workaround, try adding a unique identifier to your parameters."
        )


class SerializationError(AlgBenchError):
    """Raised when data cannot be serialized to JSON."""

    def __init__(self, data: object, original_error: Exception) -> None:
        super().__init__(
            f"Cannot serialize data of type {type(data).__name__} to JSON.\n"
            f"\n"
            f"Original error: {original_error}\n"
            f"\n"
            f"Suggestions:\n"
            f"  1. Ensure all parameters and results are JSON-serializable\n"
            f"  2. Implement __str__ or __repr__ for custom objects\n"
            f"  3. Convert objects to dictionaries before returning"
        )


class ConcurrentAccessError(DatabaseError):
    """Raised when unsafe concurrent access is detected."""

    def __init__(self, operation: str) -> None:
        super().__init__(
            f"Operation '{operation}' is not thread-safe.\n"
            f"\n"
            f"This operation cannot be performed while other processes "
            f"are accessing the database.\n"
            f"\n"
            f"Thread-safe operations: add, run, exists, __iter__\n"
            f"NOT thread-safe: compress, clear, delete, delete_if, apply"
        )


class ConfigurationError(AlgBenchError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Configuration error: {message}")
