# import uuid
# import random
import sqlite3


# def create_id() -> str:
#     return str(uuid.uuid1(random.getrandbits(48) | 0x010000000000))


def connect_to_db() -> sqlite3.Connection:
    return sqlite3.connect("scheduler.db")


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

