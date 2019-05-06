from typing import Dict, Union, List, Set, TYPE_CHECKING

from . import locationmanager, entity

if TYPE_CHECKING:
    # Needed only for typing
    from . import entityrequirement


class EntityManager:
    """
    TODO: Maybe change from name being the key in the dictionary and instead create an ID for each entity

    add_entity
    remove_entity
    get_entities
    get_entities_by_location

    add_requirement_to_entity
    remove_requirement_from_entity
    ...
    """

    def __init__(self):
        self.entities: Dict[str, entity.Entity] = {}
        self.location_manager: locationmanager.LocationManager = locationmanager.LocationManager()

    def add_entity(self, name: str) -> bool:
        temp = entity.Entity(name)
        self.entities[temp.entity_id] = temp
        return True

    def remove_entity(self, entity_id: str) -> bool:
        if entity_id in self.entities:
            del self.entities[entity_id]
            return True
        return False

    def get_entities(self) -> List[entity.Entity]:
        return list(self.entities.values())

    def get_entities_by_location(self) -> Dict[locationmanager.Location, List[entity.Entity]]:
        temp = {None: []}
        for loc in self.location_manager.locations:
            temp[loc] = []
        for entity_value in self.entities.values():
            if len(entity_value.locations) == 0:
                temp[None].append(entity_value)

            for entity_loc in entity_value.locations:
                temp[entity_loc].append(entity_value)

        return temp

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
