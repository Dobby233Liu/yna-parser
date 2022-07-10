from .genclasses import YnaError, YnaFunctionContext
from .decorators import yna_function, gettable_global, result_storable
from typing import Any, Optional
from .typechecker import get_int, get_float
from datetime import datetime, timedelta
from urllib.parse import quote as urlencode
from random import choice, choices, randrange
from fake_discord import Member

FunctionArguments = tuple[str]

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
@gettable_global
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

def _get_attr(obj: Any, attrs: str) -> Any:
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

    return _get_attr(rand_user, attrs)

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

    return _get_attr(user, attrs)

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

    if max <= min or step <= 0:
        raise YnaError("invalid range")

    return randrange(min, max, step)

@yna_function
async def set(ctx: YnaFunctionContext, name: str, value: Optional[Any] = None) -> None:
    """
    Variables can be stored using the set command and then recalled like any other Format Object.
    All objects saved this way are strings.
    """

    ctx.set_variable(name, value is not None and str(value) or None)

# func would be a special case in the parser