"""
A reasonably robust JSON-serializer. The purpose is only to save data
for  a later analysis, not to recreate it exactly.
If something cannot be converted to JSON, it is converted to str.
"""
import json


def to_json(obj):
    """
    Convert the object to a JSON-serializable object.
    """
    if obj is None:
        return None
    if isinstance(obj, float):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return {str(k): to_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_json(e) for e in obj]
    if isinstance(obj, tuple):
        return [to_json(e) for e in obj]
    return str(obj)


def to_json_str(obj):
    data = to_json(obj)
    return json.dumps(data)
