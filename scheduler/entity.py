from .entitystate import EntityState
from .entityrequirement import EntityRequirement
from typing import List
from datetime import datetime


class Entity:

    def __init__(self, name: str):
        self.name = name
        self.state: EntityState = EntityState()
        self.requirements: List[EntityRequirement] = []

    def clear_state(self) -> None:
        """
        Resets the entity state so that it looks like they were never scheduled
        """
        self.state: EntityState = EntityState()

    def cost_to_schedule(self, shift_start: datetime, shift_end: datetime) -> float:
        """
        Determines the cost to schedule an entity for a particular shift
        @TODO This does average, but would max be more fitting?
        :param shift_start: start of the shift
        :param shift_end:  end of the shift
        :return: average cost of all the requirements
        """
        total_cost = 0
        req_count = 0

        for req in self.requirements:
            if req.applies(self.state, shift_start, shift_end):
                req_count += 1
                total_cost += req.cost

        if req_count == 0:
            return 0
        else:
            return total_cost/req_count

    def schedule(self, shift_start: datetime, shift_end: datetime) -> None:
        """
        Updates the state to schedule for a particular shift
        :param shift_start:
        :param shift_end:
        """
        self.state.scheduled(shift_start, (shift_end - shift_start))

    def add_requirement(self, new_requirement: EntityRequirement):
        self.requirements.append(new_requirement)

    def remove_requirement(self, old_requirement: EntityRequirement):
        self.requirements.remove(old_requirement)
