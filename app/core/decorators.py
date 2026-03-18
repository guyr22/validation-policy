from typing import Callable

def body_rule(func: Callable) -> Callable:
    """Decorator to mark a method as a body-level rule."""
    func.__is_body_rule__ = True
    return func
