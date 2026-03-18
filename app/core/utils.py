from typing import Any, get_origin, get_args

def get_dummy_value(annotation: Any) -> Any:
    """Provides a dummy value to bypass strict validation for soft_launch/log_only."""
    origin = get_origin(annotation)
    if origin is not None:
        if origin is list: return []
        if origin is dict: return {}
        if origin is set: return set()
        from typing import Union
        if origin is Union:
            args = get_args(annotation)
            if type(None) in args: return None
            return get_dummy_value(args[0])
    if annotation is str: return ""
    if annotation is int: return 0
    if annotation is float: return 0.0
    if annotation is bool: return False
    return None
