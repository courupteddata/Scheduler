from typing import Dict, TYPE_CHECKING

from . import entitymanager, schedule

if TYPE_CHECKING:
    from . import locationmanager


class Scheduler:

    def __init__(self):
        # Use this to add and modify all of the entities
        self.entity_manager = entitymanager.EntityManager()
        self.schedule: Dict['locationmanager.Location', schedule.Schedule] = {}

    def set_schedule_for_location(self, loc: 'locationmanager.Location', sched: schedule.Schedule):
        self.schedule[loc] = sched

    def fill_schedule_for_location(self, loc: 'locationmanager.Location'):
        pass

