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

    shared.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
import sqlite3


class DB:
    ENFORCE_CONSTRAINT = 'PRAGMA foreign_keys = ON;'

    ENTITY_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS entity (' \
                          'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                          'name TEXT NOT NULL);'

    LOCATION_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS location (' \
                            'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                            'label TEXT NOT NULL);'

    ENTITY_LOCATION_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS entity_location (' \
                                   'entity_id INTEGER NOT NULL, ' \
                                   'location_id INTEGER NOT NULL, ' \
                                   'CONSTRAINT location_check_ent FOREIGN KEY(entity_id) ' \
                                   'REFERENCES entity(id) ON DELETE CASCADE, ' \
                                   'CONSTRAINT location_check_loc FOREIGN KEY(location_id) ' \
                                   'REFERENCES location(id) ON DELETE CASCADE, ' \
                                   'PRIMARY KEY(entity_id, location_id));'

    SHIFT_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS shift (' \
                         'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                         'start TEXT NOT NULL, ' \
                         'end TEXT NOT NULL, ' \
                         'info TEXT, ' \
                         'entity_id INTEGER DEFAULT NULL, ' \
                         'location_id INTEGER NOT NULL ,' \
                         'CONSTRAINT shift_check_ent FOREIGN KEY(entity_id) ' \
                         'REFERENCES entity(id) ON DELETE SET DEFAULT,' \
                         'CONSTRAINT shift_check_loc FOREIGN KEY(location_id) ' \
                         'REFERENCES location(id) ON DELETE CASCADE);'

    REQUIREMENT_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS requirement (' \
                               'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                               'entity_id INTEGER NOT NULL,' \
                               'type TEXT NOT NULL, ' \
                               'json_data TEXT NOT NULL,' \
                               'CONSTRAINT requirement_check_ent FOREIGN KEY (entity_id) ' \
                               'REFERENCES entity(id) ON DELETE CASCADE);'

    WORK_TABLE_CREATE = 'CREATE TABLE IF NOT EXISTS work (' \
                        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                        'progress REAL NOT NULL,' \
                        'message TEXT);'

    def __init__(self):
        self.db = sqlite3.connect("scheduler.db", check_same_thread=False, timeout=60)
        self.db.execute(DB.ENFORCE_CONSTRAINT)
        self.db.commit()

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
        temp.db.execute(DB.WORK_TABLE_CREATE)
        temp.db.commit()

        temp.db.close()
