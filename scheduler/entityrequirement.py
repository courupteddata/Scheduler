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

from datetime import datetime, time, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING
from dateutil import parser

if TYPE_CHECKING:
    # Needed only for typing
    from . import entitystate

"""
Contains the base requirement for units to compute cost

Flow should be:
 1) applies(entity_state: EntityState, shift_start: datetime, shift_end: datetime) -> bool
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
        self._cost = cost
        self.is_relative = is_relative

    def applies(self, entity_state: 'entitystate.EntityState', shift_start: datetime, shift_end: datetime) -> bool:
        return True

    @property
    def cost(self) -> float:
        return self._cost

    @cost.setter
    def cost(self, cost: float) -> None:
        self._cost = cost

    def serialize(self) -> dict:
        return {"label": self.label, "cost": self._cost, "is_relative": self.is_relative}

    @classmethod
    def unserialize(cls, data: dict):
        return cls(data['label'], data['cost'], data['is_relative'])


class TimeFrameRequirement(EntityRequirement):
    class Types(Enum):
        UNDEFINED = auto()
        DAY_OF_WEEK = auto()
        DATE_RANGE = auto()
        TIME_RANGE = auto()

    def __init__(self, label: str, cost: float):
        super().__init__(label, cost, False)
        self._time_frame_type = TimeFrameRequirement.Types.UNDEFINED

        # DayOfWeek Typed
        self._day_of_week: int = -1

        # DateRange Typed
        self._datetime_start: datetime = datetime.today()
        self._datetime_end: datetime = self._datetime_start

        # TimeRange Typed
        self._time_start: time = self._datetime_start.time()
        self._time_end: time = self._datetime_start.time()

    def serialize(self) -> dict:
        data = {"label": self.label,
                "cost": self.cost,
                "time_frame_type": self._time_frame_type.name,
                "is_relative": self.is_relative}

        if self._time_frame_type is TimeFrameRequirement.Types.DAY_OF_WEEK:
            data["day_of_week"] = self._day_of_week
        elif self._time_frame_type is TimeFrameRequirement.Types.DATE_RANGE:
            data["datetime_start"] = self._datetime_start.isoformat()
            data["datetime_end"] = self._datetime_end.isoformat()
        elif self._time_frame_type is TimeFrameRequirement.Types.TIME_RANGE:
            data["time_start"] = self._time_start.isoformat()
            data["time_end"] = self._time_end.isoformat()

        return data

    @classmethod
    def unserialize(cls, data: dict):
        created = cls(data["label"], data["cost"])

        if data['time_frame_type'] == TimeFrameRequirement.Types.DAY_OF_WEEK.name:
            created._day_of_week = data["day_of_week"]
            created._time_frame_type = TimeFrameRequirement.Types.DAY_OF_WEEK
        elif data['time_frame_type'] == TimeFrameRequirement.Types.DATE_RANGE.name:
            created._datetime_start = parser.parse(data["datetime_start"])
            created._datetime_end = parser.parse(data["datetime_end"])
            created._time_frame_type = TimeFrameRequirement.Types.DATE_RANGE
        elif data['time_frame_type'] == TimeFrameRequirement.Types.TIME_RANGE.name:
            created._time_start = parser.parse(data["time_start"]).time()
            created._time_end = parser.parse(data["time_end"]).time()
            created._time_frame_type = TimeFrameRequirement.Types.TIME_RANGE
        else:
            created._time_frame_type = TimeFrameRequirement.Types.UNDEFINED

        return created

    @classmethod
    def create_day_week_requirement(cls, label: str, day_of_week: datetime, cost: float):
        """

        :param label: the label to give the requirement
        :param day_of_week: a date that has the correct day of the week
        :param cost:
        :return:
        """
        created = cls(label, cost)
        created._day_of_week = day_of_week.weekday()
        created._time_frame_type = TimeFrameRequirement.Types.DAY_OF_WEEK

        return created

    @classmethod
    def create_date_range_requirement(cls, label: str, start: datetime, end: datetime, cost: float):

        if start > end:
            raise ValueError("start must be before end in the range")

        created = cls(label, cost)
        created._time_frame_type = TimeFrameRequirement.Types.DATE_RANGE
        created._datetime_start = start
        created._datetime_end = end

        return created

    @classmethod
    def create_time_range_requirement(cls, label: str, start: time, end: time, cost: float):
        # A range can span multiple days, but the importance is that it is just time

        if start == end:
            raise ValueError("start and end cannot be the same, use date range instead if needed.")

        created = cls(label, cost)
        created._time_frame_type = TimeFrameRequirement.Types.TIME_RANGE
        created._time_start = start
        created._time_end = end

        return created

    def applies(self, entity_state: 'entitystate.EntityState', shift_start: datetime, shift_end: datetime) -> bool:

        if shift_start > shift_end:
            raise ValueError("shift_start must be before shift_end")

        if self._time_frame_type is TimeFrameRequirement.Types.UNDEFINED:
            return False
        elif self._time_frame_type is TimeFrameRequirement.Types.DAY_OF_WEEK:
            return shift_start.weekday() <= self._day_of_week <= shift_end.weekday()
        elif self._time_frame_type is TimeFrameRequirement.Types.DATE_RANGE:
            # (StartA <= EndB)  and  (EndA >= StartB)
            return self._datetime_start <= shift_end and self._datetime_end >= shift_start
        elif self._time_frame_type is TimeFrameRequirement.Types.TIME_RANGE:
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
                return self._time_start <= shift_end.time() and self._time_end >= shift_start.time()


class RelativeRequirement(EntityRequirement):

    def __init__(self, label: str, cost: float):
        super().__init__(label, cost, True)
        self._distance: float = 0
        self._during: bool = False
        self._after: bool = False

    def serialize(self) -> dict:
        return {"label": self.label,
                "cost": self.cost,
                "is_relative": self.is_relative,
                "during": self._during,
                "after": self._after,
                "distance": self._distance}

    @classmethod
    def unserialize(cls, data: dict):
        created = cls(data["label"], data["cost"])
        created._during = data["during"]
        created._after = data["after"]
        created._distance = data["distance"]

        return created

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
        created._distance = (distance.total_seconds() / 3600.0)
        created._during = True

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
        created._distance = (distance.total_seconds() / 3600.0)
        created._after = True

        return created

    def applies(self, entity_state: 'entitystate.EntityState', shift_start: datetime, shift_end: datetime) -> bool:
        distance = entity_state.last_schedule_distance_hours(shift_start, shift_end)

        if distance == -1:
            return False

        if self._during:
            return distance <= self._distance
        elif self._after:
            return distance > self._distance
        else:
            return False


class TotalsRequirement(EntityRequirement):

    def __init__(self, label: str, cost: float):
        super().__init__(label, cost, True)

        self.total_requirement: float = 0
        self.is_rolling: bool = False
        self._hours_worked: float = 0
        self._scale: bool = False

        # rolling requirement
        self._start: datetime = datetime.now()
        self._length: timedelta = timedelta(days=1)

        # fixed window requirement, uses same start
        self._end: datetime = self._start

    def serialize(self) -> dict:
        return {"label": self.label,
                "cost": self._cost,
                "is_relative": self.is_relative,
                "total_requirement": self.total_requirement,
                "is_rolling": self.is_rolling,
                "scale": self._scale,
                "start": self._start.isoformat(),
                "length": self._length.total_seconds()/3600.0,
                "end": self._end.isoformat()}

    @classmethod
    def unserialize(cls, data: dict):
        created = cls(data["label"], data["cost"])
        created.total_requirement = data["total_requirement"]
        created.is_rolling = data["is_rolling"]
        created._scale = data["scale"]
        created._start = parser.parse(data["start"])
        created._length = data["length"]
        created._end =  parser.parse(data["end"])

        return created

    @classmethod
    def create_rolling_totals_requirement(cls, label: str, start: datetime, length: timedelta, total_requirement: float,
                                          cost: float, scale: bool = False):
        created = cls(label, cost)
        created._scale = scale
        created.total_requirement = total_requirement
        created.is_rolling = True

        created._start = start
        created._length = length

        return created

    @classmethod
    def create_fixed_totals_requirement(cls, label: str, start: datetime, end: datetime, total_requirement: float,
                                        cost: float, scale: bool = False):
        created = cls(label, cost)
        created._scale = scale
        created.total_requirement = total_requirement
        created.is_rolling = False

        created._start = start
        created._end = end

        return created

    def applies(self, entity_state: 'entitystate.EntityState', shift_start: datetime, shift_end: datetime) -> bool:
        if shift_start < self._start:  # Make sure that the shift start is after requirement start
            return False

        if self.is_rolling:
            window_start: datetime = self._start
            while (window_start <= shift_start <= window_start + self._length) is not True:
                window_start += self._length
            self._hours_worked = entity_state.hours_worked_in(window_start, window_start + self._length)
            return True
        else:
            if self._start <= shift_start <= self._end:
                self._hours_worked = entity_state.hours_worked_in(self._start, self._end)
                return True
            else:
                return False

    @property
    def cost(self) -> float:
        if self._scale:
            return (self._hours_worked / self.total_requirement) * self._cost

        return self._cost
