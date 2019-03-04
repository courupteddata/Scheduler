from enum import Enum, auto


class Action(Enum):
    SCHEDULE = auto()
    BEFORE = auto()
    AFTER = auto()
    AT = auto()