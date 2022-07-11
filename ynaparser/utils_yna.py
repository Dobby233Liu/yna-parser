from typing import Any
from .classes import YnaError
import inspect

def get_attr(obj: Any, attrs: str) -> Any:
    """
    Gets attribute of an object by an attribute path.
    """
    attr = obj
    for i in attrs.split("."):
        try:
            attr = getattr(attr, i)
        except AttributeError as e:
            raise YnaError("has no attrs") from e
    return attr

def is_yna_error(error: YnaError | Any):
    return isinstance(error, YnaError)

def get_int(value: Any, error: str = "non int parameter") -> int:
    """
    Gets a integer from the function parameters.
    """
    try:
        return int(value)
    except ValueError as e:
        raise YnaError(error, source_function=inspect.stack()[2][3]) from e

def get_float(value: Any, error: str = "non float parameter") -> int:
    """
    Gets a float from the function parameters.
    """
    try:
        return float(value)
    except ValueError as e:
        raise YnaError(error, source_function=inspect.stack()[2][3]) from e