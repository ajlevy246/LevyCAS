"""Set of utility functions and decorators for LevyCAS."""

def singleton(cls):
    """Ensure only one instance of a class exists."""
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper 