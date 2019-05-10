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
