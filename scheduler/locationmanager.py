from typing import Set, List, TYPE_CHECKING

if TYPE_CHECKING:
    # Needed only for typing
    from . import entity


class Location:

    def __init__(self, label: str):
        self.label = label

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.label == other.label
        else:
            return NotImplemented


class LocationManager:

    def __init__(self):
        self.locations: Set[Location] = set()

    def add_location(self, loc: Location) -> bool:
        """
        Adds a location but, returns false if the item was already apart of the locations available
        :param loc: the location to add
        :return: true if added and didn't exist, false otherwise
        """
        was_in = loc in self.locations
        if not was_in:  # Not needed, but no need to run add if it was already in set
            self.locations.add(loc)
            return True
        return False

    def set_entity_locations(self, locations: Set[Location], entity_to_set: 'entity.Entity') -> bool:
        if locations.issubset(self.locations):
            entity_to_set.locations = locations
            return True

        return False

    def remove_location(self, loc: Location) -> bool:
        """
        Removes a location
        :param loc: location to remove
        :return: True if the location was removed, false otherwise (like if it was never a valid location)
        """
        was_in = loc in self.locations
        if was_in:
            self.locations.remove(loc)
        return was_in

    def get_locations(self) -> List[Location]:
        return list(self.locations)
