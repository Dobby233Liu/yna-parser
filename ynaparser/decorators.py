from types import FunctionType
from typing import Optional
from .classes import YnaError, YnaFunctionContext
from functools import update_wrapper

def yna_function(func: FunctionType) -> FunctionType:
    """
    When a function has this decorator, it is treated as a function
    in the YNA language.
    """

    return func

def global_variable_getter(func: FunctionType) -> FunctionType:
    """
    When a function has this decorator, it will called
    when accessed as a global variable.
    """

    return func

def result_storable(func: Optional[FunctionType] = None, *, type_clash=False) -> FunctionType:
    """
    When a function has this decorator, then when the function is invoked like:

        {func<k>:[...];}

    its return value will be stored into the variable k.

    If type_clash is true, the function errors when it's not called
    as a global variable.
    """

    def inner(ctx: YnaFunctionContext, *args: tuple[str], **kwargs: tuple[str]) -> str:
        # I hate squas
        if type_clash and not ctx.called_as_variable:
            raise YnaError("type clash")

        ret = func(ctx, *args, **kwargs)

        if ctx.set_return(ret):
            return None
        return ret

    if func is None:
        def decorator(func):
            return update_wrapper(inner, func)
        return decorator
    return update_wrapper(inner, func)