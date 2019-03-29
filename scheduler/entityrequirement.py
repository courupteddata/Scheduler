from .entitystate import EntityState
from datetime import datetime, time, timedelta
from enum import Enum, auto

"""
Contains the base requirement for units to compute cost

Flow should be:
 1) applies(self, entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool
 if True:
 2) EntityRequirement().cost [to get the cost]

different creation methods exist:

TimeFrameRequirement:
1) create_day_week_requirement(label: str, start: datetime, end: datetime, cost: float)
2) create_date_range_requirement(label: str, start: datetime, end: datetime, cost: float)
3) create_time_range_requirement(cls, label: str, start: time, end: time, cost: float)

RelativeRequirement:
1)

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
    class Types(Enum):
        UNDEFINED = auto()
        DAY_OF_WEEK = auto()
        DATE_RANGE = auto()
        TIME_RANGE = auto()

    def __init__(self, label: str, cost: float):
        super().__init__(label, cost, False)
        self.time_frame_type = TimeFrameRequirement.Types.UNDEFINED

        # DayOfWeek Typed
        self.day_of_week: int

        # DateRange Typed
        self.datetime_start: datetime
        self.datetime_end: datetime

        # TimeRange Typed
        self.time_start: time
        self.time_end: time

    @classmethod
    def create_day_week_requirement(cls, label: str, day_of_week: datetime, cost: float):
        """

        :param label: the label to give the requirement
        :param day_of_week: a date that has the correct day of the week
        :param cost:
        :return:
        """
        created = cls(label, cost)
        created.day_of_week = day_of_week.weekday()
        created.time_frame_type = TimeFrameRequirement.Types.DAY_OF_WEEK

        return created

    @classmethod
    def create_date_range_requirement(cls, label: str, start: datetime, end: datetime, cost: float):

        if start > end:
            raise ValueError("start must be before end in the range")

        created = cls(label, cost)
        created.time_frame_type = TimeFrameRequirement.Types.DATE_RANGE
        created.datetime_start = start
        created.datetime_end = end

        return created

    @classmethod
    def create_time_range_requirement(cls, label: str, start: time, end: time, cost: float):
        # A range can span multiple days, but the importance is that it is just time

        if start == end:
            raise ValueError("start and end cannot be the same, use date range instead if needed.")

        created = cls(label, cost)
        created.time_frame_type = TimeFrameRequirement.Types.TIME_RANGE
        created.time_start = start
        created.time_end = end

        return created

    def applies(self, entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool:

        if shift_start > shift_end:
            raise ValueError("shift_start must be before shift_end")

        if self.time_frame_type is TimeFrameRequirement.Types.UNDEFINED:
            return False
        elif self.time_frame_type is TimeFrameRequirement.Types.DAY_OF_WEEK:
            return shift_start.weekday() <= self.day_of_week <= shift_end.weekday()
        elif self.time_frame_type is TimeFrameRequirement.Types.DATE_RANGE:
            # (StartA <= EndB)  and  (EndA >= StartB)
            return self.datetime_start <= shift_end and self.datetime_end >= shift_start
        elif self.time_frame_type is TimeFrameRequirement.Types.TIME_RANGE:
            # 11pm to 11pm is invalid
            """
            start  end
              |------|
            what if the shift is 24 hours? this breaks, assume that one that spans 24 hours or more to encompass' time
            86400 seconds in a day   
            """
            if (shift_end - shift_start).total_seconds() >= 86400.0:
                return True
            else:
                return self.time_start <= shift_end.time() and self.time_end >= shift_start.time()


class RelativeRequirement(EntityRequirement):

    def __init__(self, label: str, cost: float):
        super().__init__(label, cost, True)
        self.distance: timedelta

    @classmethod
    def create_relative_requirement(cls, label: str, distance: timedelta, cost: float):
        created = cls(label, cost)
        created.distance = distance

        return created

    def applies(self, entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool:
        return (entity_state.last_schedule - shift_start) >= self.distance
