from typing import TYPE_CHECKING, List, Tuple
import heapq
from . import entitymanager, shiftmanager, locationmanager

if TYPE_CHECKING:
    from . import entity


class Scheduler:

    def __init__(self, max_cost: float = 10, step_size: float = .5):
        # Use this to add and modify all of the entities
        self.entity_manager = entitymanager.EntityManager()
        self.shift_manager = shiftmanager.ShiftManager()
        self.location_manager = locationmanager.LocationManager()
        self.step_size = step_size
        self.max_cost = max_cost


    def fill_schedule_for_location(self, location_id: int) -> int:
        current_cost_limit = self.step_size


        while current_cost_limit <= self.max_cost and num_empty_shifts > 0:
            num_empty_shifts = 0
            for shift in self.schedule[loc].shifts:
                if shift.filled:
                    continue

                count = 0
                options = []

                for person in entities:
                    count += 1
                    cost_to_schedule = person.cost_to_schedule(shift.start, shift.end)
                    heapq.heappush(options, (cost_to_schedule, count, person))

                cost, _, best_person = heapq.heappop(options)

                if cost <= current_cost_limit:
                    best_person.schedule(shift.start, shift.end)
                    shift.filled = best_person.entity_id
                else:
                    num_empty_shifts += 1
            current_cost_limit += self.step_size

        return True, f"Schedule for location {loc.label} done, with {num_empty_shifts} empty shifts"

    def fill_schedules(self) -> List[Tuple[bool, str]]:
        entities_by_location = self.entity_manager.get_entities_by_location()
        to_return = []

        count = 0
        locs = []
        for key in self.schedule:
            if key in entities_by_location:
                heapq.heappush(locs, (len(entities_by_location[key]), count, key))
                count += 1

        ordered_locs = [heapq.heappop(locs)[2] for _ in range(len(locs))]

        for loc in ordered_locs:
            to_return.append(self.fill_schedule_for_location(loc, entities_by_location[loc]))

        return to_return
