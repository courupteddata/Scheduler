from typing import List, Union
import sqlite3


ENTITY_TABLE_CREATE = '''CREATE TABLE IF NOT EXISTS entity (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);'''
LOCATION_TABLE_CREATE = '''CREATE TABLE IF NOT EXISTS location (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT);'''
ENTITY_LOCATION_TABLE_CREATE = '''CREATE TABLE IF NOT EXISTS entity_location (entity_id INTEGER, 
                                                                              location_id INTEGER, UNIQUE(entity_id, 
                                                                              location_id));'''
SHIFT_TABLE_CREATE = '''CREATE TABLE IF NOT EXISTS shift (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                          start TEXT NOT NULL, 
                                                          end TEXT NOT NULL,
                                                          info TEXT,
                                                          entity_id TEXT);'''
REQUIREMENTS_TABLE_CREATE = '''CREATE TABLE IF NOT EXISTS entity (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                 type TEXT NOT NULL, 
                                                                 json_data BLOB);'''


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
        self.connection = sqlite3.connect("scheduler.db")
        self.connection.execute(LOCATION_TABLE_CREATE)
        self.connection.execute(ENTITY_LOCATION_TABLE_CREATE)
        self.connection.commit()

    def add_location(self, label: str) -> int:
        """
        Adds a location, always works if the database is working
        :param label: the location to add
        :return: returns the integer id of the item just added
        """
        inserted_id = self.connection.execute('INSERT INTO location(label) VALUES (?);', (label,)).lastrowid
        self.connection.commit()

        return inserted_id

    def remove_location(self, location_id: int) -> bool:
        """
        Removes a location
        :param location_id: location to remove
        :return: True if the location was removed, false otherwise (like if it was never a valid location)
        """
        return self.connection.execute('DELETE FROM location WHERE id=?;', (location_id,)).rowcount == 1

    def get_locations(self) -> List[Location]:
        all_locations = []
        for loc in self.connection.execute('SELECT id,label FROM location;'):
            all_locations.append(Location(loc[1], loc[0]))
        return all_locations

    def get_location_by_location_id(self, location_id: int) -> Union[Location, None]:
        data = self.connection.execute('SELECT id,label FROM location WHERE id=?;',
                                       (location_id,)).fetchone()
        if data is None:
            return None
        else:
            return Location(data[1], data[0])

    def get_entity_id_by_location_id(self, location_id: int) -> List[int]:
        to_return = []
        for item in self.connection.execute('SELECT entity_id FROM entity_location WHERE location_id=?;',
                                            (location_id,)):
            to_return.append(item[0])
        return to_return

    def get_location_id_by_entity_id(self, entity_id: int) -> List[int]:
        to_return = []
        for item in self.connection.execute('SELECT location_id from entity_location WHERE entity_id=?;', (entity_id,)):
            to_return.append(item[0])
        return to_return

    def add_location_to_entity(self, location_id: Union[int, List[int]], entity_id: Union[int, List[int]]) -> int:
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

        to_return = self.connection.executemany("INSERT OR IGNORE INTO "
                                                "entity_location(entity_id, location_id) VALUES (?, ?);",
                                                modified_list).rowcount
        self.connection.commit()
        return to_return

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

        to_return = self.connection.executemany("DELETE from entity_location WHERE entity_id=? AND location_id=?;",
                                                modified_list).rowcount
        self.connection.commit()
        return to_return


if __name__ == '__main__':
    test = LocationManager()
    #print(test.add_location("testing"))

    print(test.get_locations())
    print(test.remove_location(10))
    print(test.get_locations())

    print(test.get_location_by_location_id(1))
