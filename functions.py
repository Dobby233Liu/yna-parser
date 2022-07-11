from multiprocessing.sharedctypes import Value
from .classes import YnaContext, YnaError, YnaFunctionContext
from .decorators import yna_function, global_variable_getter, result_storable
from typing import Any, Optional, Type
from .types_transformer import get_int, get_float
from datetime import datetime, timedelta
from urllib.parse import quote as urlencode
from random import choice, choices, randrange
from fake_discord import Member
from .utils import get_attr, is_yna_error
from enum import Enum
import re

FunctionArguments = tuple[str]

class YnaWhenOperator(Enum):
    # Checks that a and b are the same.
    EQUAL = "eq"
    # Checks that a and b are different.
    NOT_EQUAL = "ne"
    # Checks that a is strictly less than b.
    LESSER_THAN = "lt"
    # Checks that a is less than or equal to b.
    LESSER_THAN_OR_EQUAL = "le"
    # Checks that a is strictly greater than b.
    GREATER_THAN = "gt"
    # Checks that a is greater than or equal to b.
    GREATER_THAN_OR_EQUAL = "ge"
    # Checks that a is a substring of b.
    # Checks that a matches an element in the comma seperated list in b.
    IS_IN = "in"
    # Checks that a is of the type defined in b
    IS = "is"

class YnaWhenTypes(Enum):
    # Checks if a is a single word.
    WORD = "word"
    # Checks if a is a single letter.
    LETTER = "letter"
    # Checks if a is castable to int.
    NUMBER = "number"
    # Checks if a is castable to float.
    DECIMAL = "decimal"
    # Checks if a is a yna exception.
    ERROR = "error"
    # /regex/ Checks if a matches the regex.

## Evaluation Objects ##############################

## Case Functions
## Case functions change the case of a block of evaluated content,
## either to UPPER, lower or Title case.

@yna_function
async def upper(ctx: YnaFunctionContext, content: str) -> str:
    """
    Change the case of a block of evaluated content
    to UPPER case.
    """
    return content.upper()

@yna_function
async def lower(ctx: YnaFunctionContext, content: str) -> str:
    """
    Change the case of a block of evaluated content
    to lower case.
    """
    return content.lower()

@yna_function
async def title(ctx: YnaFunctionContext, content: str) -> str:
    """
    Change the case of a block of evaluated content
    to Title case.
    """
    return content.title()

@yna_function
async def len(ctx: YnaFunctionContext, content: str) -> int:
    """
    Gets the length of the given evaluated content.
    """
    return len(content)

@yna_function
async def slice(ctx: YnaFunctionContext, *args: tuple[int, str] | tuple[Optional[int], Optional[int], int, str]) -> str:
    """
    Slices a piece of evaluated content.

    slice(ctx, index, content)
        - returns a specific 0-indexed character

    slice(ctx, b=None, e=None, s=1, content)
        - returns a 0-indexed, top-exclusive substring
    """

    if len(args) == 2:
        index, content = args
        index = get_int(index)
        return content[index]

    b, e, s, content = args
    b, e, s = (
        b and get_int(b, error="non int index") or None,
        e and get_int(e, error="non int index") or None,
        s and get_int(s, error="non int index") or 1
    )
    return content[b:e:s]

@yna_function
@global_variable_getter
@result_storable
async def time(ctx: YnaFunctionContext, offset: int = 0, template: str = "%H:%M") -> str:
    """
    Gets the current time.
    """

    offset = get_int(offset, error="invalid offset")
    time = datetime.now()
    try:
        time += timedelta(hours=offset)
    except ValueError as e:
        raise YnaError("invalid offset") from e
    except TypeError as e:
        raise YnaError("invalid offset") from e

    try:
        return ("{:%s}" % template).format(time)
    except ValueError as e:
        raise YnaError("invalid format") from e

@yna_function
async def parse(ctx: YnaFunctionContext, quote: str) -> str:
    """
    Converts characters into a string into a format that can be used in URLs.
    """

    if not quote:
        raise YnaError("no content")
    return urlencode(quote)

@yna_function
@result_storable
async def choose(ctx: YnaFunctionContext, *options: tuple) -> str:
    """
    Chooses a random element from a given list.
    """

    if not options or len(options) <= 0:
        raise YnaError("no options")

    return choice(options)

@yna_function
@result_storable
async def wchoose(ctx: YnaFunctionContext, *options: tuple) -> str:
    """
    Chooses an element with regards to given weightings.

    wchoose(ctx, option: Any, weight: float, ...)
    """

    if not options or len(options) <= 0:
        raise YnaError("no options")
    if len(options) % 2 != 0:
        raise YnaError("mismatched weightings")

    population = options[::2]
    weights = options[1::2]
    weights = map(lambda x: get_float(x, error="invalid weight"), weights)

    return choices(population, weights)

@yna_function
@result_storable
async def user(ctx: YnaFunctionContext, attrs: str = None, *args: Optional[FunctionArguments]) -> Member | Any:
    """
    Chooses a random member from the server.
    Can choose any member, not just online/active/in the channel members.
    """

    if args and len(args) > 0:
        raise YnaError("too many args")

    rand_user = choice(ctx.base_ctx.get_members())
    if not attrs or not attrs.strip():
        return rand_user

    return get_attr(rand_user, attrs, func_context=True)

@yna_function
@result_storable
async def nameof(ctx: YnaFunctionContext, id: int, attrs: str = None, *args: Optional[FunctionArguments]) -> str | Any:
    """
    Fetches a members name from their ID.
    This can be paired with `member` to get an object.
    """

    if args and len(args) > 0:
        raise YnaError("too many args")
    if not id:
        raise YnaError("no id")

    id = get_int(id, "no id")
    user = ctx.base_ctx.get_member(id)
    if not user:
        raise YnaError("not found")

    if not attrs or not attrs.strip():
        return str(user)

    return get_attr(user, attrs, func_context=True)

@yna_function
@result_storable
async def num(ctx: YnaFunctionContext, min: int = 0, max: int = 100, step: int = 1) -> int:
    """
    Gets a random number between a given range.
    """

    min, max, step = (
        get_int(min, error="invalid args"),
        get_int(max, error="invalid args"),
        get_int(step, error="invalid args"),
    )

    try:
        return randrange(min, max, step)
    except ValueError as e:
        raise YnaError("invalid range") from e
    except TypeError as e:
        raise YnaError("invalid range") from e

@yna_function
async def set(ctx: YnaFunctionContext, name: str, value: Optional[Any] = None) -> None:
    """
    Variables can be stored using the set command and then recalled like any other Format Object.
    All objects saved this way are strings.
    """

    ctx.base_ctx.set_variable(name, value and str(value) or None)

@yna_function
async def member(ctx: YnaFunctionContext, key: str, name: str) -> None:
    """
    Variables can be stored using the set command and then recalled like any other Format Object.
    All objects saved this way are strings.
    """

    member = ctx.base_ctx.get_member_named(name)
    if not member:
        raise YnaError("not found")

    ctx.base_ctx.set_variable(key, member)

# func would be a special case in the parser

def _empty_cb(ctx: YnaContext) -> None:
    pass

# special case: parser evaluates on_true and on_false to functions
@yna_function
async def when(ctx: YnaFunctionContext, arg1: Any, op: YnaWhenOperator, arg2: Any | YnaWhenTypes, on_true: function, on_false: Optional[function] = None) -> Optional[Any]:
    on_false = on_false and on_false or _empty_cb

    condition = False
    match op:
        case YnaWhenOperator.EQUAL.value:
            condition = arg1 == arg2
        case YnaWhenOperator.NOT_EQUAL.value:
            condition = arg1 != arg2
        case YnaWhenOperator.LESSER_THAN.value:
            condition = get_int(arg1, "args must be numbers") < get_int(arg2, "args must be numbers")
        case YnaWhenOperator.LESSER_THAN_OR_EQUAL.value:
            condition = get_int(arg1, "args must be numbers") <= get_int(arg2, "args must be numbers")
        case YnaWhenOperator.GREATER_THAN.value:
            condition = get_int(arg1, "args must be numbers") > get_int(arg2, "args must be numbers")
        case YnaWhenOperator.GREATER_THAN_OR_EQUAL.value:
            condition = get_int(arg1, "args must be numbers") >= get_int(arg2, "args must be numbers")
        case YnaWhenOperator.IS_IN.value:
            try:
                if "," in arg2:
                    arg2 = arg2.split(",")
                condition = arg1 in arg2
            except ValueError as e:
                raise YnaError("args do not support in") from e
            except TypeError as e:
                raise YnaError("args do not support in") from e
        case YnaWhenOperator.IS.value:
            match arg2:
                case YnaWhenTypes.WORD.value:
                    # https://stackoverflow.com/a/27280836
                    condition = len(arg1.split()) == 1
                case YnaWhenTypes.LETTER.value:
                    condition = arg1.isalpha()
                case YnaWhenTypes.NUMBER.value:
                    condition = True
                    try:
                        int(arg1)
                    except ValueError:
                        condition = False
                case YnaWhenTypes.DECIMAL.value:
                    condition = True
                    try:
                        float(arg1)
                    except ValueError:
                        condition = False
                case YnaWhenTypes.ERROR.value:
                    condition = is_yna_error(arg1)
                case _:
                    if arg2.startswith("/") and arg2.endswith("/"):
                        try:
                            condition = bool(re.match(arg1[1:-1], arg1))
                        except re.error as e:
                            raise YnaError("invalid regex") from e
                    else:
                        raise YnaError("invalid type name")
        case _:
            raise YnaError("invalid op")

    if condition:
        return on_true(ctx.base_ctx)
    else:
        return on_false(ctx.base_ctx)

# TODO: the rest of functions