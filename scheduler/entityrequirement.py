"""
    This file is part of Scheduler.

    Scheduler is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Scheduler is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Scheduler.  If not, see <https://www.gnu.org/licenses/>.

    entityrequirement.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""

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
1) create_relative_during_requirement(cls, label: str, distance: timedelta, cost: float):
2) create_relative_after_requirement(cls, label: str, distance: timedelta, cost: float):

TotalsRequirement:
1) create_rolling_totals_requirement(cls, label: str, start: datetime, length: timedelta, total_requirement: float,
                                          cost: float, scale: bool = False):
2) create_fixed_totals_requirement(cls, label: str, start: datetime, end: datetime, total_requirement: float,
                                        cost: float, scale: bool = False):

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
        self.day_of_week: int = -1

        # DateRange Typed
        self.datetime_start: datetime = datetime.today()
        self.datetime_end: datetime = self.datetime_start

        # TimeRange Typed
        self.time_start: time = self.datetime_start.time()
        self.time_end: time = self.datetime_start.time()

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
        self.distance: timedelta = timedelta(days=1)
        self.during: bool = False

    @classmethod
    def create_relative_during_requirement(cls, label: str, distance: timedelta, cost: float):
        """
        Creates a requirement cost that applies during the timedelta
        :param label:
        :param distance:
        :param cost:
        :return:
        """
        created = cls(label, cost)
        created.distance = distance
        created.during = True

        return created

    @classmethod
    def create_relative_after_requirement(cls, label: str, distance: timedelta, cost: float):
        """
        Creates a requirement cost that applies after the timedelta
        :param label:
        :param distance:
        :param cost:
        :return:
        """
        created = cls(label, cost)
        created.distance = distance
        created.during = False

        return created

    def applies(self, entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool:
        if self.during:
            return (entity_state.last_schedule - shift_start) <= self.distance
        else:
            return (entity_state.last_schedule - shift_start) >= self.distance


class TotalsRequirement(EntityRequirement):

    def __init__(self, label: str, cost: float):
        super().__init__(label, cost, True)

        self.scale: bool = False
        self.total_requirement: float = 0
        self.is_rolling: bool = False
        self.hours_worked: float = 0
        self.saved_cost: float = cost

        # rolling requirement
        self.start: datetime = datetime.now()
        self.length: timedelta = timedelta(days=1)

        # fixed window requirement, uses same start
        self.end: datetime = self.start

    @classmethod
    def create_rolling_totals_requirement(cls, label: str, start: datetime, length: timedelta, total_requirement: float,
                                          cost: float, scale: bool = False):
        created = cls(label, cost)
        created.scale = scale
        created.total_requirement = total_requirement
        created.is_rolling = True

        created.start = start
        created.length = length

        return created

    @classmethod
    def create_fixed_totals_requirement(cls, label: str, start: datetime, end: datetime, total_requirement: float,
                                        cost: float, scale: bool = False):
        created = cls(label, cost)
        created.scale = scale
        created.total_requirement = total_requirement
        created.is_rolling = False

        created.start = start
        created.end = end

        return created

    def applies(self, entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool:
        if shift_start < self.start:  # Make sure that the shift start is after requirement start
            return False

        if self.is_rolling:
            window_start: datetime = self.start
            while (window_start <= shift_start <= window_start + self.length) is not True:
                window_start += self.length
            self.hours_worked = entity_state.hours_worked_in(window_start, window_start + self.length)
            return True
        else:
            if self.start <= shift_start <= self.end:
                self.hours_worked = entity_state.hours_worked_in(self.start, self.end)
                return True
            else:
                return False

    @property
    def cost(self) -> float:
        if self.scale:
            return (self.hours_worked / self.total_requirement) * self.saved_cost

        return self.saved_cost
