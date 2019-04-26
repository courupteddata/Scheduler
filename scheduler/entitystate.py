from datetime import datetime, timedelta
from typing import List


class EntityState:
    class WorkedEntry:
        """
        Contains a sortable entry based on the shift start datetime.
        Also keeps track of the number of hours worked for a particular shift
        """

        def __init__(self, shift_start: datetime, hours_worked: float):
            self.shift_start = shift_start
            self.hours_worked = hours_worked

        def __lt__(self, other) -> bool:
            if isinstance(other, EntityState.WorkedEntry):
                return self.shift_start < other.shift_start
            else:
                return NotImplemented

    def __init__(self):
        self.hours_worked: List[EntityState.WorkedEntry] = []
        # self._last_schedule: datetime = datetime(year=1, month=1, day=1)

    def scheduled(self, shift_start: datetime, hours_worked: [float, timedelta]) -> None:
        if isinstance(hours_worked, timedelta):
            self.hours_worked.append(EntityState.WorkedEntry(shift_start, hours_worked.total_seconds() / 3600.0))
        else:
            self.hours_worked.append(EntityState.WorkedEntry(shift_start, hours_worked))

        # self.last_schedule = shift_start

    def hours_worked_in(self, start: datetime, end: datetime) -> float:
        # TODO: Change hours worked to a more efficient data structure for this operation
        total = 0
        for entry in self.hours_worked:
            if start <= entry.shift_start <= end:
                total += entry.hours_worked
        return total

    def last_schedule_distance_hours(self, start: datetime, end: datetime) -> float:
        # Added because what if we are filling in a spot and don't know the order
        # TODO: optimize this
        min_distance = 1000
        for entry in self.hours_worked:
            min_distance = min(
                min_distance,
                abs((entry.shift_start - start).total_seconds() / 3600.0),
                abs(((entry.shift_start + timedelta(hours=entry.hours_worked)) - end).total_seconds() / 3600.0))

        return min_distance
