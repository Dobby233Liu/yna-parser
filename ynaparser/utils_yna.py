from typing import Any
from .classes import YnaError

def get_attr(obj: Any, attrs: str, func_context: bool = False) -> Any:
    """
    Gets attribute of an object by an attribute path.
    """
    attr = obj
    for i in attrs.split("."):
        try:
            attr = getattr(attr, i)
        except AttributeError as e:
            if func_context:
                raise YnaError("has no attrs") from e
            else:
                raise e
    return attr

def is_yna_error(error: YnaError | Any):
    return isinstance(error, YnaError)