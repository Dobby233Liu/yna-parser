from operator import attrgetter
from typing import Any, Callable, Iterable, Optional, TypeVar
from classes import YnaError

T = TypeVar('T')

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

def get(iterable: Iterable[T], /, **attrs: Any) -> Optional[T]:
    # global -> local
    _all = all

    # Special case the single element call
    if len(attrs) == 1:
        k, v = attrs.popitem()
        pred = attrgetter(k.replace('__', '.'))
        return next((elem for elem in iterable if pred(elem) == v), None)

    converted = [(attrgetter(attr.replace('__', '.')), value) for attr, value in attrs.items()]
    for elem in iterable:
        if _all(pred(elem) == value for pred, value in converted):
            return elem
    return None

def find(predicate: Callable[[T], Any], iterable: Iterable[T], /) -> Optional[T]:
    return next((element for element in iterable if predicate(element)), None)

def is_yna_error(error: YnaError | Any):
    return isinstance(error, YnaError)