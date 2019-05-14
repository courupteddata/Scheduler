"""
    This file is part of Scheduler.

    Scheduler is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Scheduler is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Scheduler.  If not, see <https://www.gnu.org/licenses/>.

    entity.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    # Needed only for typing
    from . import entityrequirement


class Entity:

    def __init__(self, name: str, entity_id: int):
        self.name = name
        self.entity_id = entity_id
        self.requirements: List['entityrequirement.EntityRequirement'] = []
