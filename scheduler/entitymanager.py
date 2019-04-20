from typing import Dict, Union, List, TYPE_CHECKING

from . import locationmanager, entity

if TYPE_CHECKING:
    # Needed only for typing
    from . import entityrequirement


class EntityManager:
    """
    add_entity
    remove_entity
    add_requirement_to_entity
    remove_requirement_from_entity

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

    def get_entities(self) -> entity.Entity:
        return list(self.entities.values())[0]

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
