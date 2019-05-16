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

    entitymanager.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from typing import Tuple, Union, List, TYPE_CHECKING, Dict
from . import shared, entitystate
from datetime import datetime
from threading import Lock

from . import entity, requirementhelper

if TYPE_CHECKING:
    # Needed only for typing
    from . import entityrequirement


class EntityManager:

    def __init__(self):
        self.connection = shared.DB().get_connection()
        shared.DB.create_all_tables()
        self.connection_modify_lock = Lock()

    def create_entity(self, name: str) -> int:
        with self.connection_modify_lock:
            inserted_id = self.connection.execute('INSERT INTO entity(name) VALUES (?);', (name,)).lastrowid
            self.connection.commit()

        return inserted_id

    def update_entity_name(self, entity_id: int, name: str):
        with self.connection_modify_lock:
            modified_row_count = self.connection.execute('UPDATE entity SET name=? WHERE id=?;', (name, entity_id)).rowcount
            self.connection.commit()

        return modified_row_count

    def delete_entity(self, entity_id: int) -> bool:
        with self.connection_modify_lock:
            modified_row_count = self.connection.execute('DELETE FROM entity WHERE id=?;', (entity_id,)).rowcount
            self.connection.commit()

        return modified_row_count > 0

    def get_entity(self) -> List[Dict]:
        return [{"entity_id": ent[0], "entity_name": ent[1]} for ent
                in self.connection.execute('SELECT id,name FROM entity;').fetchall()]

    def get_entity_by_id(self, entity_id: int, include_requirements: bool = True) -> Union[None, entity.Entity]:
        data = self.connection.execute('SELECT name FROM entity WHERE id=?;', (entity_id,)).fetchone()

        if data is None:
            return None
        name = data[0]

        created_entity = entity.Entity(name, entity_id)

        if not include_requirements:
            return created_entity

        requirements = self.get_requirements_for_entity(entity_id)

        if len(requirements) == 0:
            return created_entity

        created_entity.requirements = list(zip(*requirements))[2]

        return created_entity

    def get_cost_to_schedule(self, ent: entity.Entity, shift_start: datetime, shift_end: datetime) -> float:
        total_cost = 0
        req_count = 0

        state = entitystate.EntityState(self.connection, ent.entity_id)

        for req in ent.requirements:
            if req.applies(state, shift_start, shift_end):
                req_count += 1
                total_cost += float(req.cost)

        if req_count == 0:
            return 0
        else:
            return total_cost / req_count

    """
    Requirement management of an entity
    """
    def add_requirement_to_entity(self, entity_id: int, requirement: 'entityrequirement.EntityRequirement') -> int:
        return requirementhelper.store_requirement(self.connection, entity_id, requirement, self.connection_modify_lock)

    def delete_requirement(self, requirement_id: Union[int, List[int]]) -> int:

        with self.connection_modify_lock:
            if isinstance(requirement_id, list):
                to_return = self.connection.executemany("DELETE FROM requirement WHERE id=?", requirement_id).rowcount
            else:
                to_return = self.connection.execute("DELETE FROM requirement WHERE id=?", (requirement_id,)).rowcount
            self.connection.commit()

        return to_return

    def get_requirements_for_entity(self, entity_id: int) -> \
            List[Tuple[int, str, 'entityrequirement.EntityRequirement']]:

        data = self.connection.execute("SELECT id,type,json_data "
                                       "FROM requirement WHERE entity_id=?", (entity_id,)).fetchall()

        if len(data) == 0:
            return []

        return [(req[0], req[1], requirementhelper.rebuild_from_data(req[1], req[2], req[0])) for req in data]

    def get_requirement_id(self, requirement_id: int) -> Union[Tuple[str, 'entityrequirement.EntityRequirement'], None]:
        data = self.connection.execute("SELECT type,json_data FROM requirement "
                                       "WHERE id=?;", (requirement_id,)).fetchone()

        if data is None:
            return None

        return data[0], requirementhelper.rebuild_from_data(data[0], data[1], requirement_id)

    def get_location_for_entity(self, entity_id: int) -> List[Dict]:
        locations = self.connection.execute("SELECT location_id FROM entity_location WHERE entity_id=?;",
                                            (entity_id,)).fetchall()

        if len(locations) == 0:
            return []

        data = []

        for loc in locations:
            temp = self.connection.execute('SELECT id,label FROM location WHERE id=?;', loc).fetchone()
            if temp is not None:
                data.append(temp)

        return [{"location_id": item[0], "location_label": item[1]} for item in data]

    def get_stats_for_entity(self, entity_id: int, start: datetime = None, end: datetime = None) -> List[Dict]:

        where_query_string = ""
        query_data = ()
        previous = True

        where_query_string += " entity_id=?"
        query_data += (entity_id,)

        if start is not None:
            if previous:
                where_query_string += " AND"
            previous = True
            where_query_string += " start >= datetime(?)"
            query_data += (start.isoformat(),)

        if end is not None:
            if previous:
                where_query_string += " AND"
            where_query_string += " start <= datetime(?)"
            query_data += (end.isoformat(),)

        if where_query_string != "":
            where_query_string = " WHERE" + where_query_string

        return [{"location_id": data[0], "shift_count": data[1], "total_hours": data[2]} for data in
                self.connection.execute(f"SELECT location_id,COUNT(*),"
                                        f"SUM(strftime(\'%s\', end) - strftime(\'%s\', start))/3600.0 FROM shift "
                                        f"{ where_query_string } GROUP BY location_id;", query_data).fetchall()]
