from typing import List, Set, TYPE_CHECKING
from datetime import datetime
import uuid
import random

from . import entitystate

if TYPE_CHECKING:
    # Needed only for typing
    from . import locationmanager, entityrequirement


class Entity:

    def __init__(self, name: str):
        self.name = name
        self.state: entitystate.EntityState = entitystate.EntityState()
        self.requirements: List['entityrequirement.EntityRequirement'] = []
        self.locations: Set['locationmanager.Location'] = set()
        self.entity_id = str(uuid.uuid1(random.getrandbits(48) | 0x010000000000))

    def clear_state(self) -> None:
        """
        Resets the entity state so that it looks like they were never scheduled
        """
        self.state: entitystate.EntityState = entitystate.EntityState()

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

    def add_requirement(self, new_requirement: 'entityrequirement.EntityRequirement'):
        self.requirements.append(new_requirement)

    def remove_requirement(self, old_requirement: 'entityrequirement.EntityRequirement'):
        self.requirements.remove(old_requirement)
