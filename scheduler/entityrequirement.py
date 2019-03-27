from .entitystate import EntityState
from datetime import datetime, time
from enum import Enum,auto

"""
Contains the base requirement for units to compute cost
"""


class EntityRequirement:
    def __init__(self, label: str, cost: float):
        self.label = label
        self.cost = cost

    def applies(self, entity_state: EntityState) -> bool:
        return True


class TimeFrameRequirement(EntityRequirement):

    class TimeFrameTypes(Enum):
        UNDEFINED = auto
        DAY_OF_WEEK = auto
        DATE_RANGE = auto
        TIME_RANGE = auto

    def __init__(self, label: str, cost: float):
        super().__init__(label, cost)
        self.time_frame_type = TimeFrameRequirement.TimeFrameTypes.UNDEFINED

        # DayOfWeek Typed
        day_of_week : int = -1



    @classmethod
    def create_day_week_requirement(cls, label: str, day_of_week: datetime.date, cost: float):
        """

        :param label: the label to give the requirement
        :param day_of_week: a date that has the correct day of the week
        :param cost:
        :return:
        """
        created = cls(label, cost)


        return created

    def applies(self, entity_state: EntityState) -> bool:
        if self.time_frame_type == TimeFrameRequirement.TimeFrameTypes.UNDEFINED:
            return False

