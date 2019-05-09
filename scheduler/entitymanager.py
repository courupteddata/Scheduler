from typing import Tuple, Union, List, Set, TYPE_CHECKING
from . import shared

from . import locationmanager, entity

if TYPE_CHECKING:
    # Needed only for typing
    from . import entityrequirement


class EntityManager:

    def __init__(self):
        self.connection = shared.DB().get_connection()
        shared.DB.create_all_tables()

    def create_entity(self, name: str) -> int:
        inserted_id = self.connection.execute('INSERT INTO entity(name) VALUES (?);', (name,)).lastrowid
        self.connection.commit()

        return inserted_id

    def delete_entity(self, entity_id: int) -> bool:
        modified_row_count = self.connection.execute('DELETE FROM entity WHERE id=?;', (entity_id,)).rowcount
        self.connection.commit()

        return modified_row_count > 0

    def get_entity(self) -> List[Tuple[int, str]]:
        return [(ent[0], ent[1]) for ent in self.connection.execute('SELECT id,name FROM entity;')]

    def build_entity_by_id(self, entity_id: int):
        pass



    """
    Requirement management of an entity
    """
    def add_requirement_to_entity(self, entity_id: str,
                                  requirement: Union['entityrequirement.EntityRequirement',
                                                     List['entityrequirement.EntityRequirement']]) -> bool:
        if entity_id not in self.entities:
            return False
        if not isinstance(requirement, list):
            self.entities[entity_id].add_requirement(requirement)
        else:
            for req in requirement:
                self.entities[entity_id].add_requirement(req)
        return True

    def remove_requirement_from_entity(self, entity_id: str,
                                       requirement: Union['entityrequirement.EntityRequirement',
                                                          List['entityrequirement.EntityRequirement']]) -> bool:
        if entity_id not in self.entities:
            return False
        if not isinstance(requirement, list):
            self.entities[entity_id].remove_requirement(requirement)
        else:
            for req in requirement:
                self.entities[entity_id].remove_requirement(req)
        return True

    def get_requirements_for_entity(self, entity_id: str) -> List['entityrequirement.EntityRequirement']:
        return self.entities[entity_id].requirements

    """
    Location management of an entity
    """
    def add_location(self, loc: locationmanager.Location):
        return self.location_manager.add_location(loc)

    def remove_location(self, loc: locationmanager.Location):
        return self.location_manager.remove_location(loc)

    def get_locations(self) -> List[locationmanager.Location]:
        return self.location_manager.get_locations()

    def add_locations_to_entity(self, entity_id: str, loc_set: Set[locationmanager.Location]) -> bool:
        return self.location_manager.set_entity_locations(self.entities[entity_id].locations | loc_set,
                                                          self.entities[entity_id])

    def remove_locations_from_entity(self, entity_id: str, loc_set: Set[locationmanager.Location]) -> bool:
        return self.location_manager.set_entity_locations(self.entities[entity_id].locations - loc_set,
                                                          self.entities[entity_id])
