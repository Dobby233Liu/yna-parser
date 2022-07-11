from math import ceil, floor, inf
from types import FunctionType
from .classes import YnaBaseContext, YnaError, YnaFunctionContext, YnaSubContext
from .decorators import yna_function, global_variable_getter, result_storable
from typing import Any, Optional
from .types_transformer import get_int, get_float
from datetime import datetime, timedelta
from urllib.parse import quote as urlencode
from random import choice, choices, randrange
from .fake_discord import Member
from .utils_yna import get_attr, is_yna_error
from enum import Enum
import re

FunctionArguments = tuple[str]
ParamString = str

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
async def slice(ctx: YnaFunctionContext, args: ParamString, content: str) -> str:
    """
    Slices a piece of evaluated content.

    slice(ctx, index, content)
        - returns a specific 0-indexed character

    slice(ctx, "b=None,e=None,s=1", content)
        - returns a 0-indexed, top-exclusive substring
    """

    args = args.split(",")

    if len(args) <= 0:
        raise YnaError("no args")
    if len(args) == 2:
        raise YnaError("bad content")
    if len(args) > 3:
        raise YnaError("too many nums")
    if len(args) == 1:
        index = get_int(args, "non int index")
        try:
            return content[index]
        except IndexError as e:
            raise YnaError("bad index") from e

    b, e, s = args
    b, e, s = (
        b and get_int(b, error="non int index") or None,
        e and get_int(e, error="non int index") or None,
        s and get_int(s, error="non int index") or 1
    )
    if s <= 0:
        raise YnaError("zero step")

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

def _empty_cb(ctx: YnaBaseContext) -> None:
    pass

# special case: interpreter evaluates on_true and on_false to functions
@yna_function
async def when(ctx: YnaFunctionContext, arg1: Any, op: YnaWhenOperator, arg2: Any | YnaWhenTypes, on_true: FunctionType, on_false: Optional[FunctionType] = None) -> Optional[Any]:
    """
    Conditionals, similar to if statements.
    """

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

# special case:
#   - interpreter evaluates content to a function
#   - handles this generator
@yna_function
async def loop(ctx: YnaFunctionContext, args: ParamString, content: FunctionType) -> Optional[any]:
    """
    Flow control, similar to "for" loops.
    Whilst inside the loop, your current loopcount will be stored in the {iter} variable. Note: This will be deleted when a loop is exited.
    When loops are nested, only the current loop value is stored in {iter}. Once the loop finishes, the loop value of the outside loop will be copied back again.
    If you want to access the loop variable inside nested loops, you will need to {set} it to a new variable.
    """

    context = YnaSubContext(ctx.base_ctx)

    args = args.split(",")

    if len(args) <= 0 or len(args) > 3:
        raise YnaError("invalid args")

    b = None
    e = None
    s = None
    if len(args) == 1:
        e = get_int(args, "non int index")
    else:
        b, e, s = args
        b, e, s = (
            b and get_int(b, error="non int index") or 1,
            get_int(e, error="non int index"),
            s and get_int(s, error="non int index") or 1
        )

    for i in range(b, e, s):
        # TODO: prevent iter from leaking out
        # see also YnaSubContext init
        context.set_variable("iter", i)
        yield content(context)

@yna_function
async def rep(ctx: YnaFunctionContext, var: str, *args: tuple[str]) -> str:
    """
    Works like a find and replace function in a text editor.
    This command has 2 different syntaxes. The old and depreciated one and a new one.
    Switching between the two is done by setting the {newrep} variable.
    """

    if ctx.root_ctx.new_replace:
        with_str, in_str = args
    else:
        in_str, with_str = args
    return in_str.replace(var, with_str)

@yna_function
async def split(ctx: YnaFunctionContext, var: str, content: str, sep: str = ",") -> int:
    """
    Splits a string based on a given separator, generating a set of variables with the split values.
    Each element of the output will be saved in a variable with a given prefix, and counting up from 1.
    This function returns the total number of elements (which is by definition the highest valid output index.)
    """

    result = content.split(sep)
    for i in range(len(result)):
        ctx.base_ctx.set_variable(var + str(i), result[i])
    return len(result)

@yna_function
async def math(ctx: YnaFunctionContext, op: str, *args: tuple[int | float]) -> int | float:
    """
    All arithmetic is done through a single function.
    Each method takes a specific number of arguments and has a specific resolution.
    The resolution is either int or float, the args are either exactly 1, exactly 2 or 2 and more.

    You can use aliases, e.e. add and +, not and ~
    """

    if not args or len(args) < 1:
        raise YnaError("no args")

    def ensure_arg_amount(len):
        if len(args) < len:
            raise YnaError("invalid args")
    def ensure_args_float():
        for i in range(len(args)):
            args[i] = get_float(args[i], "non-float args")
    def ensure_args_int():
        for i in range(len(args)):
            args[i] = get_int(args[i], "non-int args")

    # aliases
    match op:
        case "+":
            op = "add"
        case "-":
            op = "sub"
        case "*":
            op = "mul"
        case "/":
            op = "div"
        case "/f":
            op = "div"
        case "//":
            op = "idiv"
        case "%":
            op = "mod"
        case "**":
            op = "pow"
        case "&":
            op = "and"
        case "|":
            op = "or"
        case "^":
            op = "xor"
        case "~":
            op = "not"

    try:
        match op:
            case "add":
                ensure_arg_amount(2)
                ensure_args_float()
                resolution = args[0]
                for i in args[1:]:
                    resolution += i
            case "sub":
                ensure_arg_amount(2)
                ensure_args_float()
                resolution = args[0] - args[1]
            case "mul":
                ensure_arg_amount(2)
                ensure_args_float()
                resolution = args[0]
                for i in args[1:]:
                    resolution *= i
            case "div":
                ensure_arg_amount(2)
                ensure_args_float()
                resolution = args[0] / args[1]
            case "idiv":
                ensure_arg_amount(2)
                ensure_args_int()
                resolution = args[0] // args[1]
            case "mod":
                ensure_arg_amount(2)
                ensure_args_int()
                resolution = args[0] % args[1]
            case "pow":
                ensure_arg_amount(2)
                ensure_args_float()
                resolution = args[0] ** args[1]
            case "and":
                ensure_arg_amount(2)
                ensure_args_int()
                resolution = args[0]
                for i in args[1:]:
                    resolution &= i
            case "or":
                ensure_arg_amount(2)
                ensure_args_int()
                resolution = args[0]
                for i in args[1:]:
                    resolution |= i
            case "xor":
                ensure_arg_amount(2)
                ensure_args_int()
                resolution = args[0] ^ args[1]
            case "not":
                ensure_arg_amount(1)
                ensure_args_int()
                resolution = args[0]
            case "max":
                ensure_arg_amount(2)
                ensure_args_float()
                resolution = max(*args)
            case "min":
                ensure_arg_amount(2)
                ensure_args_float()
                resolution = min(*args)
            case "floor":
                ensure_arg_amount(1)
                ensure_args_float()
                resolution = floor(args[0])
            case "ceil":
                ensure_arg_amount(1)
                ensure_args_float()
                resolution = ceil(args[0])
            case "round":
                ensure_arg_amount(1)
                ensure_args_float()
                resolution = round(args[0])
            case _:
                raise YnaError("unknon op")
    except ZeroDivisionError as e:
        raise YnaError("divide by 0") from e

    if resolution >= inf:
        raise YnaError("inf")
    elif resolution <= -inf:
        raise YnaError("-inf")

    return resolution

# oneline is special case in parser

async def void(ctx: YnaFunctionContext, content: Any):
    """
    This evaluates its internal code and then swallows the output.
    The output will be printed to the debug log
    """
    # TODO: debug log
    pass

# TODO: the rest of functions