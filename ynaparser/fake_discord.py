from typing import List, Dict, Optional
from . import utils

class User(object):
    """
    A fake user for message responses
    """

    id: int
    name: str
    discriminator: str

    def __init__(self, id: int, name: str, discriminator: str) -> None:
        self.id = id
        self.name = name
        self.discriminator = discriminator

    def __int__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return f"{self.name}#{self.discriminator}"

class Member(object):
    """
    A fake member for message responses
    """

    nick: str = None
    _user: User

    def __init__(self, user: User, nick: Optional[str] = None) -> None:
        self._user = user
        self.nick = nick

    @property
    def display_name(self) -> str:
        return self._nick and self._nick or self._user.name

    def __int__(self) -> int:
        return int(self._user)

    def __str__(self) -> str:
        return str(self._user)

class Guild(object):
    """
    A fake guild for message responses
    """

    _members: Dict[int, Member]

    def __init__(self, members: Dict[int, Member] = []) -> None:
        self._members = members

    @property
    def members(self) -> List[Member]:
        return list(self._members.values())

    def get_member(self, id: int) -> Optional[Member]:
        return self._members.get(id)

    def get_member_named(self, name: str) -> Optional[Member]:
        result = None
        members = self.members
        if len(name) > 5 and name[-5] == '#':
            potential_discriminator = name[-4:]

            result = utils.get(members, name=name[:-5], discriminator=potential_discriminator)
            if result is not None:
                return result

        def pred(m: Member) -> bool:
            return m.nick == name or m.name == name

        return utils.find(pred, members)

class Context(object):
    """
    A fake "context" for message responses
    """

    guild: Guild = None

    def __init__(self, guild: Guild) -> None:
        self.guild = guild