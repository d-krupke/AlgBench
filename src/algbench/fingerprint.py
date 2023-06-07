import hashlib

from .db.json_serializer import to_json_str


def fingerprint(data) -> str:
    """
    Create a fingerprint of data.
    """
    return hashlib.sha1(to_json_str(data).encode()).hexdigest()
