from . import shiftmanager
from typing import Dict, Tuple, Union


class ScheduleManager:
    def __init__(self):
        self.schedules: Dict[str, shiftmanager.Schedule] = {}

    def get_schedule(self, schedule_id) -> Tuple[bool, Union[shiftmanager.Schedule, None]]:
        if schedule_id in self.schedules:
            return True, self.schedules[schedule_id]
        return False, None

    def delete_schedule(self, schedule_id) -> bool:
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            return True
        return False
