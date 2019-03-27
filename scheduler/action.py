from enum import Enum, auto


class Action(Enum):
    SCHEDULE = auto()


class TimeAction(Enum):
    AT = auto()
    BEFORE = auto()
    AFTER = auto()

