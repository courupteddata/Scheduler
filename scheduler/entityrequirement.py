from .entitystate import EntityState
from datetime import datetime, time
from enum import Enum, auto

"""
Contains the base requirement for units to compute cost

different creation methods exist:

TimeFrameRequirement:
1) create_day_week_requirement(label, day_of_week, cost)

"""


class EntityRequirement:
    def __init__(self, label: str, cost: float, is_relative: bool = False):
        self.label = label
        self.cost = cost
        self.is_relative = is_relative

    def applies(self, entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool:
        return True

    @property
    def cost(self) -> float:
        return self.cost

    @cost.setter
    def cost(self, cost: float) -> None:
        self.cost = cost


class TimeFrameRequirement(EntityRequirement):
    class TimeFrameTypes(Enum):
        UNDEFINED = auto
        DAY_OF_WEEK = auto
        DATE_RANGE = auto
        TIME_RANGE = auto

    def __init__(self, label: str, cost: float, is_relative: bool = False):
        super().__init__(label, cost, is_relative)
        self.time_frame_type = TimeFrameRequirement.TimeFrameTypes.UNDEFINED

        # DayOfWeek Typed
        self.day_of_week: int = -1

    @classmethod
    def create_day_week_requirement(cls, label: str, day_of_week: datetime, cost: float):
        """

        :param label: the label to give the requirement
        :param day_of_week: a date that has the correct day of the week
        :param cost:
        :return:
        """
        created = cls(label, cost, False)
        created.day_of_week = day_of_week.weekday()

        return created

    @classmethod
    def create_date_range_requirement(cls, label: str, day_of_week: datetime, cost: float):
        # TODO: Finish this.
        pass

    def applies(self, entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool:
        if self.time_frame_type == TimeFrameRequirement.TimeFrameTypes.UNDEFINED:
            return False
        elif self.time_frame_type == TimeFrameRequirement.TimeFrameTypes.DAY_OF_WEEK:
            return shift_start.weekday() <= self.day_of_week <= shift_end.weekday()
