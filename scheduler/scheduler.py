from threading import Thread
import heapq
from . import entitymanager, shiftmanager, locationmanager, workmanager
from typing import List, Tuple


class Scheduler:

    def __init__(self, max_cost: float = 10, step_size: float = .5):
        # Use this to add and modify all of the entities
        self.entity_manager = entitymanager.EntityManager()
        self.shift_manager = shiftmanager.ShiftManager()
        self.location_manager = locationmanager.LocationManager()
        self.work_manager = workmanager.WorkManager()
        self.step_size = step_size
        self.max_cost = max_cost

    def fill_schedule_for_location(self, location_id: int, work_id: int) -> int:
        current_cost_limit = self.step_size

        entities = [self.entity_manager.get_entity_by_id(entity_id) for entity_id
                    in self.location_manager.get_entity_ids_by_location_id(location_id)]
        shifts = self.shift_manager.get_empty_shift_by_location_id(location_id)
        num_empty_shifts = self.shift_manager.get_empty_shift_count_by_location_id(location_id)

        location_name = self.location_manager.get_locations_by_location_id(location_id)
        starting_empty = num_empty_shifts

        while current_cost_limit <= self.max_cost and num_empty_shifts > 0:
            for shift in shifts:
                count = 0
                options = []

                for person in entities:
                    if person is None:
                        continue
                    count += 1
                    cost_to_schedule = self.entity_manager.get_cost_to_schedule(person, shift.start, shift.end)
                    heapq.heappush(options, (cost_to_schedule, count, person))

                cost, _, best_person = heapq.heappop(options)

                if cost <= current_cost_limit:
                    self.shift_manager.fill_shift_by_id(shift.shift_id, best_person.entity_id)

            current_cost_limit += self.step_size
            shifts = self.shift_manager.get_empty_shift_by_location_id(location_id)
            num_empty_shifts = self.shift_manager.get_empty_shift_count_by_location_id(location_id)
            self.work_manager.update_work_entry(work_id, num_empty_shifts/starting_empty,
                                                f"Still working... There are still {num_empty_shifts} "
                                                f"empty shifts for location: {location_name}.")

        self.work_manager.update_work_entry(work_id, num_empty_shifts / starting_empty,
                                            f"Done... There are still {num_empty_shifts} "
                                            f"empty shifts for location {location_name}.")

        return num_empty_shifts

    def fill_schedules(self) -> int:

        order = []
        count = 0

        locations = self.location_manager.get_locations()
        for loc in locations:
            heapq.heappush(order, (len(self.location_manager.get_entity_ids_by_location_id(loc.location_id)),
                                   count, loc.location_id, loc.label))
            count += 1

        count = 0
        for _ in range(len(order)):
            temp = heapq.heappop(order)
            work_id = self.work_manager.add_work_entry(f"Starting work on location: {temp[3]}")
            count += self.fill_schedule_for_location(temp[2], work_id)

        return count

    def fill_schedule_on_separate_thread(self, location_id: int) -> int:
        location_label = self.location_manager.get_locations_by_location_id(location_id).label

        work_id = self.work_manager.add_work_entry(f"Starting work on location: {location_label}")

        Thread(target=self.fill_schedule_for_location, args=(self, location_id, work_id)).start()

        return work_id

    def fill_list_of_schedules(self, to_schedule: List[Tuple[int, int]]):
        for item in to_schedule:
            self.fill_schedule_for_location(item[0], item[1])

    def fill_schedules_on_separate_thread(self):

        order = []
        count = 0

        locations = self.location_manager.get_locations()
        for loc in locations:
            heapq.heappush(order, (len(self.location_manager.get_entity_ids_by_location_id(loc.location_id)),
                                   count, loc.location_id, loc.label))
            count += 1

        work = []

        for _ in range(len(order)):
            temp = heapq.heappop(order)
            work_id = self.work_manager.add_work_entry(f"Starting work on location: {temp[3]}")
            work.append((temp[2], work_id))

        Thread(target=self.fill_list_of_schedules, args=(self, work)).start()

        #  Returns list of (location_id, work_id)
        return work
