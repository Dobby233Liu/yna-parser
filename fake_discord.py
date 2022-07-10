from typing import List, Dict, Optional

class Member(object):
    """
    A fake member for message responses
    """

    def __init__(self, id: int) -> None:
        pass

class Guild(object):
    """
    A fake guild for message responses
    """

    _members: Dict[int, Member] = []

    def __init__(self, members: Dict[int, Member] = []) -> None:
        self._members = members

    @property
    def members(self) -> List[Member]:
        return list(self._members.values())

    def get_member(self, id: int) -> Optional[Member]:
        return self._members.get(id)

class Context(object):
    """
    A fake "context" for message responses
    """

    guild: Guild = None

    def __init__(self, guild: Guild) -> None:
        self.guild = guild