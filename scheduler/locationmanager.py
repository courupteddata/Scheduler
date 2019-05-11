from typing import List, Union
from . import shared


class Location:

    def __init__(self, label: str, location_id: int):
        self.label = label
        self.location_id = location_id

    def __hash__(self):
        return hash((self.label, self.location_id))

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.label == other.label and self.location_id == other.location_id
        else:
            return NotImplemented

    def __repr__(self):
        return f"label= {self.label}, location_id= {self.location_id}\n"


class LocationManager:

    def __init__(self):
        self.connection = shared.DB().get_connection()
        shared.DB.create_all_tables()

    def create_location(self, label: str) -> int:
        """
        Adds a location, always works if the database is working
        :param label: the location to add
        :return: returns the integer id of the item just added
        """
        inserted_id = self.connection.execute('INSERT INTO location(label) VALUES (?);', (label,)).lastrowid
        self.connection.commit()

        return inserted_id

    def update_location(self, location_id: int, new_label: str) -> bool:
        modified_row_count = self.connection.execute('UPDATE location SET label=? WHERE id=?',
                                                     (new_label, location_id)).rowcount
        self.connection.commit()

        return modified_row_count > 0

    def delete_location(self, location_id: int) -> bool:
        """
        Removes a location
        :param location_id: location to remove
        :return: True if the location was removed, false otherwise (like if it was never a valid location)
        """
        modified_row_count = self.connection.execute('DELETE FROM location WHERE id=?;', (location_id,)).rowcount
        self.connection.commit()
        return modified_row_count > 0

    def get_locations(self) -> List[Location]:
        return [Location(loc[1], loc[0]) for loc in self.connection.execute('SELECT id,label FROM location;')]

    def get_locations_by_location_id(self, location_id: int) -> Union[Location, None]:
        data = self.connection.execute('SELECT id,label FROM location WHERE id=?;',
                                       (location_id,)).fetchone()
        if data is None:
            return None
        else:
            return Location(data[1], data[0])

    def get_entity_ids_by_location_id(self, location_id: int) -> List[int]:
        return [item[0] for item in
                self.connection.execute('SELECT entity_id FROM entity_location WHERE location_id=?;', (location_id,))]

    def get_location_ids_by_entity_id(self, entity_id: int) -> List[int]:
        return [item[0] for item in
                self.connection.execute('SELECT location_id from entity_location WHERE entity_id=?;', (entity_id,))]

    def add_location_to_entity(self, location_id: Union[int, List[int]], entity_id: Union[int, List[int]]) -> int:
        """
        :param location_id:
        :param entity_id:
        :return: number of rows modified
        """
        location_is_list = isinstance(location_id, list)
        entity_is_list = isinstance(entity_id, list)

        if location_is_list:
            valid_location_test = self.connection.executemany("SELECT id FROM location WHERE id=?;",
                                                              [(temp,) for temp in location_id]).fetchall()
            if len(valid_location_test) != len(location_id):
                return 0
        else:
            valid_location_test = self.connection.execute("SELECT id FROM location WHERE id=?;",
                                                          (location_id,)).fetchone()
            if valid_location_test is None:
                return 0

        if entity_is_list:
            valid_entity_test = self.connection.executemany("SELECT id FROM entity WHERE id=?;",
                                                            [(temp,) for temp in entity_id]).fetchall()
            if len(valid_entity_test) != len(entity_id):
                return 0
        else:
            valid_entity_test = self.connection.execute("SELECT id FROM entity WHERE id=?;",
                                                        (entity_id,)).fetchone()
            if valid_entity_test is None:
                return 0

        modified_list = []
        if entity_is_list:
            for ent_id in entity_id:
                if location_is_list:
                    for loc_id in location_id:
                        modified_list.append((ent_id, loc_id))
                else:
                    modified_list.append((ent_id, location_id))
        else:
            if location_is_list:
                for loc_id in location_id:
                    modified_list.append((entity_id, loc_id))
            else:
                modified_list.append((entity_id, location_id))

        row_count = self.connection.executemany('INSERT OR IGNORE INTO entity_location'
                                                '(entity_id, location_id) VALUES (?, ?);',
                                                modified_list).rowcount
        self.connection.commit()
        return row_count

    def remove_location_from_entity(self, location_id: Union[int, List[int]], entity_id: Union[int, List[int]]) -> int:
        """
        :param location_id:
        :param entity_id:
        :return: number of rows modified
        """
        location_is_list = isinstance(location_id, list)
        entity_is_list = isinstance(entity_id, list)

        modified_list = []
        if entity_is_list:
            for ent_id in entity_id:
                if location_is_list:
                    for loc_id in location_id:
                        modified_list.append((ent_id, loc_id))
                else:
                    modified_list.append((ent_id, location_id))
        else:
            if location_is_list:
                for loc_id in location_id:
                    modified_list.append((entity_id, loc_id))
            else:
                modified_list.append((entity_id, location_id))

        row_count = self.connection.executemany('DELETE from entity_location WHERE entity_id=? AND location_id=?;',
                                                modified_list).rowcount
        self.connection.commit()
        return row_count
