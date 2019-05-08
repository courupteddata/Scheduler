# import uuid
# import random
import sqlite3


# def create_id() -> str:
#     return str(uuid.uuid1(random.getrandbits(48) | 0x010000000000))

class DB:
    ENTITY_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS entity (' \
                          'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                          'name TEXT NOT NULL);'

    LOCATION_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS location (' \
                            'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                            'label TEXT NOT NULL);'

    ENTITY_LOCATION_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS entity_location (' \
                                   'entity_id INTEGER NOT NULL, ' \
                                   'location_id INTEGER NOT NULL, ' \
                                   'FOREIGN KEY(entity_id) REFERENCES entity(id) ON DELETE CASCADE, ' \
                                   'FOREIGN KEY(location_id) REFERENCES location(id) ON DELETE CASCADE, ' \
                                   'PRIMARY KEY(entity_id, location_id));'

    SHIFT_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS shift (' \
                         'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                         'start TEXT NOT NULL, ' \
                         'end TEXT NOT NULL, ' \
                         'info TEXT, ' \
                         'entity_id INTEGER DEFAULT NULL, ' \
                         'location_id INTEGER NOT NULL ,' \
                         'FOREIGN KEY(entity_id) REFERENCES entity(id) ON DELETE SET DEFAULT,' \
                         'FOREIGN KEY(location_id) REFERENCES location(id) ON DELETE CASCADE);'

    REQUIREMENT_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS requirement (' \
                               'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                               'entity_id INTEGER NOT NULL,' \
                               'type TEXT NOT NULL, ' \
                               'json_data BLOB NOT NULL,' \
                               'FOREIGN KEY (entity_id) REFERENCES entity(id) ON DELETE CASCADE);'

    def __init__(self):
        self.db = sqlite3.connect("scheduler.db")

    def get_connection(self) -> sqlite3.Connection:
        return self.db

    @classmethod
    def create_all_tables(cls) -> None:
        temp = cls()

        temp.db.execute(DB.ENTITY_TABLE_CREATE)
        temp.db.execute(DB.LOCATION_TABLE_CREATE)
        temp.db.execute(DB.ENTITY_LOCATION_TABLE_CREATE)
        temp.db.execute(DB.SHIFT_TABLE_CREATE)
        temp.db.execute(DB.REQUIREMENT_TABLE_CREATE)
        temp.db.commit()

        temp.db.close()
