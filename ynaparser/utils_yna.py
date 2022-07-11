from typing import Any
from .classes import YnaError
import inspect

def get_caller_name():
    return inspect.getouterframes(inspect.currentframe(), 2)[2].function

def get_attr(obj: Any, attrs: str, source_function=None) -> Any:
    """
    Gets attribute of an object by an attribute path.
    """
    source_function = source_function and source_function or get_caller_name()
    attr = obj
    for i in attrs.split("."):
        try:
            attr = getattr(attr, i)
        except AttributeError as e:
            raise YnaError("has no attrs", source_function=source_function) from e
    return attr

def is_yna_error(error: YnaError | Any):
    return isinstance(error, YnaError)

def get_int(value: Any, error: str = "non int parameter", source_function=None) -> int:
    """
    Gets a integer from the function parameters.
    """
    source_function = source_function and source_function or get_caller_name()
    try:
        return int(value)
    except ValueError as e:
        raise YnaError(error, source_function=source_function) from e

def get_float(value: Any, error: str = "non float parameter", source_function=None) -> int:
    """
    Gets a float from the function parameters.
    """
    source_function = source_function and source_function or get_caller_name()
    try:
        return float(value)
    except ValueError as e:
        raise YnaError(error, source_function=source_function) from e