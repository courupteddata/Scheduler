from datetime import datetime
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
        self.last_schedule: datetime = None

    def scheduled(self, shift_start: datetime, hours_worked: float) -> None:
        self.hours_worked.append(EntityState.WorkedEntry(shift_start, hours_worked))
        self.last_schedule = shift_start

    def hours_worked_in(self, start: datetime, end: datetime) -> float:
        # TODO: Change hours worked to a more efficient data structure for this operation
        total = 0
        for entry in self.hours_worked:
            if start <= entry.shift_start <= end:
                total += entry.hours_worked
        return total
