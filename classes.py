from typing import Optional, Any
from .fake_discord import Context as DiscordContext
from .fake_discord import Guild, Member

class YnaBaseContext(object):

    """
    TODO
    """
    pass

class YnaContext(YnaBaseContext):

    """
    TODO
    """

    discord_ctx: Any | DiscordContext = None

    def __init__(self, ctx: Any | DiscordContext) -> None:
        """
        Initalizes the context with ctx as the parent context.
        """

        super().__init__()

        self.discord_ctx = ctx

    variables: list[str] = []

    def set_variable(self, name, value):
        self.variables[name] = str(value)
        if value is None:
            self.variables.pop(name)

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
        Dummy function, returns a empty list.
        """
        return self.discord_ctx.guild.get_member(id)

class YnaSubContext(YnaContext):

    """
    TODO
    """
    pass

class YnaFunctionContext(YnaBaseContext):

    """
    TODO
    """

    # The parent context of the context.
    base_ctx: YnaContext = None

    # Is this function invoked by an access of it as a global variable
    # or not.
    called_as_variable: bool = False

    # The variable to set to the return value of the function.
    ret_var: str = None

    def __init__(self, ctx: YnaContext, called_as_variable: Optional[bool] = False, ret_var: Optional[str] = None) -> None:
        """
        Initalizes the context with ctx as the parent context.
        """

        super().__init__()

        self.base_ctx = ctx
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
    pass