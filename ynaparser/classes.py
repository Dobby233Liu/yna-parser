import inspect
from typing import Optional, Any
from .fake_discord import Context as DiscordContext
from .fake_discord import Member

__all__ = [
    "YnaBareContext", "YnaBaseContext",
    "YnaRootContext", "YnaSubContext",
    "YnaFunctionContext",
    "YnaError",
] 

class YnaBareContext(object):

    """
    The true base context
    """
    pass

class YnaBaseContext(YnaBareContext):

    """
    TODO
    """

    variables: list[str] = []

    def set_variable(self, name, value):
        # todo: check name vaildity

        if name == "newrep":
            self.root_ctx.new_replace = value
        if value is None:
            self.variables.pop(name)
            return
        self.variables[name] = value

class YnaRootContext(YnaBaseContext):

    """
    TODO
    """

    discord_ctx: Any | DiscordContext = None

    # The base context of the context.
    base_ctx: YnaBaseContext = None
    # The root context of the context.
    root_ctx: YnaBaseContext = None

    new_replace = False

    def __init__(self, discord_ctx: Any | DiscordContext) -> None:
        """
        Initalizes the context with ctx as the parent context.
        """

        super().__init__()

        self.discord_ctx = discord_ctx
        self.base_ctx = self
        self.root_ctx = self

    # Discord-related functions

    def get_members(self) -> list:
        """
        Returns all members of the guild the bot is in.
        Dummy function, returns a empty list.
        """
        return self.discord_ctx.guild.members

    def get_member(self, id: int) -> Optional[Member]:
        """
        Returns all members of the guild the bot is in.
        """
        return self.discord_ctx.guild.get_member(id)

    def get_member_named(self, name: str) -> Optional[Member]:
        """
        Returns the first member found that matches the name provided.
        """
        return self.discord_ctx.guild.get_member_named(id)

class YnaSubContext(YnaBaseContext):

    """
    TODO
    """

    def __init__(self, ctx: YnaBaseContext) -> None:
        """
        Initalizes the context with ctx as the parent context.
        """

        super().__init__()

        self.base_ctx = ctx
        if not isinstance(ctx, YnaSubContext):
            self.root_ctx = ctx
        else:
            while isinstance(self.root_ctx, YnaSubContext):
                self.root_ctx = ctx.base_ctx
        self.variables = ctx.variables # TODO: ???

class YnaFunctionContext(YnaBareContext):

    """
    TODO
    """

    # The parent context of the context.
    base_ctx: YnaBaseContext = None
    # The parent context of the context.
    root_ctx: YnaRootContext = None

    # Is this function invoked by an access of it as a global variable
    # or not.
    called_as_variable: bool = False

    # The variable to set to the return value of the function.
    ret_var: str = None

    def __init__(self, ctx: YnaBaseContext, called_as_variable: Optional[bool] = False, ret_var: Optional[str] = None) -> None:
        """
        Initalizes the context with ctx as the parent context.
        """

        self.base_ctx = ctx
        self.root_ctx = ctx
        if isinstance(ctx, YnaSubContext):
            while isinstance(self.root_ctx, YnaSubContext):
                self.root_ctx = ctx.base_ctx
        self.called_as_variable = called_as_variable
        self.ret_var = ret_var

    def set_return(self, value: Any):
        if self.ret_var is None:
            return False

        self.base_ctx.set_variable(self.ret_var, value)
        return True


class YnaError(Exception):
    """
    An error that ocurred when running a YNA function.
    This is not a fatal exception.
    """

    source_function: str = ""

    def __init__(self, *args: tuple, source_function: str | None = None) -> None:
        super().__init__(*args)
        self.source_function = source_function and source_function or inspect.getouterframes(inspect.currentframe(), 2)[1].function

    def __str__(self) -> str:
        return self.source_function and "<%s:%s>" % (self.source_function, super().__str__()) or "<%s>" % (super().__str__())