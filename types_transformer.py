from typing import Any
from .classes import YnaError

def get_int(value: Any, error: str = "non int parameter") -> int:
    """
    Gets a integer from the function parameters.
    """
    try:
        return int(value)
    except ValueError as e:
        raise YnaError(error) from e

def get_float(value: Any, error: str = "non float parameter") -> int:
    """
    Gets a float from the function parameters.
    """
    try:
        return float(value)
    except ValueError as e:
        raise YnaError(error) from e