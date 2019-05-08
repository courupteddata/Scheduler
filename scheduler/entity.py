from typing import List, Set, TYPE_CHECKING
from datetime import datetime
import uuid
import random

from . import entitystate

if TYPE_CHECKING:
    # Needed only for typing
    from . import entityrequirement


class Entity:

    def __init__(self, name: str, entity_id: int):
        self.name = name
        self.entity_id = entity_id
        self.requirements: List['entityrequirement.EntityRequirement'] = []

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

    def add_requirement(self, new_requirement: 'entityrequirement.EntityRequirement'):
        self.requirements.append(new_requirement)

    def remove_requirement(self, old_requirement: 'entityrequirement.EntityRequirement'):
        self.requirements.remove(old_requirement)
