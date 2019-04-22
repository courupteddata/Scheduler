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
        if name in self.entities:
            return False
        self.entities[name] = entity.Entity(name)
        return True

    def remove_entity(self, name: str) -> bool:
        if name in self.entities:
            del self.entities[name]
            return True
        return False

    def get_entities(self) -> List[entity.Entity]:
        return list(self.entities.values())

    def get_entities_by_location(self) -> Dict[str, List[entity.Entity]]:
        temp = {"None": []}
        for loc in self.location_manager.locations:
            temp[loc.label] = []
        for entity_value in self.entities.values():
            if len(entity_value.locations) == 0:
                temp["None"].append(entity_value)

            for entity_loc in entity_value.locations:
                temp[entity_loc.label].append(entity_value)

        return temp

    """
    Requirement management of an entity
    """
    def add_requirement_to_entity(self, name: str,
                                  requirement: Union['entityrequirement.EntityRequirement',
                                                     List['entityrequirement.EntityRequirement']]) -> bool:
        if name not in self.entities:
            return False
        if not isinstance(requirement, list):
            self.entities[name].add_requirement(requirement)
        else:
            for req in requirement:
                self.entities[name].add_requirement(req)
        return True

    def remove_requirement_from_entity(self, name: str,
                                       requirement: Union['entityrequirement.EntityRequirement',
                                                          List['entityrequirement.EntityRequirement']]) -> bool:
        if name not in self.entities:
            return False
        if not isinstance(requirement, list):
            self.entities[name].remove_requirement(requirement)
        else:
            for req in requirement:
                self.entities[name].remove_requirement(req)
        return True

    def get_requirements_for_entity(self, name: str) -> List['entityrequirement.EntityRequirement']:
        return self.entities[name].requirements

    """
    Location management of an entity
    """
    def add_location(self, loc: locationmanager.Location):
        return self.location_manager.add_location(loc)

    def remove_location(self, loc: locationmanager.Location):
        return self.location_manager.remove_location(loc)

    def get_locations(self) -> List[locationmanager.Location]:
        return self.location_manager.get_locations()

    def add_locations_to_entity(self, name: str, loc_set: Set[locationmanager.Location]) -> bool:
        return self.location_manager.set_entity_locations(self.entities[name].locations | loc_set, self.entities[name])

    def remove_locations_from_entity(self, name: str, loc_set: Set[locationmanager.Location]) -> bool:
        return self.location_manager.set_entity_locations(self.entities[name].locations - loc_set, self.entities[name])
