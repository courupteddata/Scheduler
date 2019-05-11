from datetime import datetime
import sqlite3


class EntityState:
    def __init__(self, db_connection: sqlite3.Connection, entity_id: int):
        self.db_connection = db_connection
        self.entity_id = entity_id

    def hours_worked_in(self, start: datetime, end: datetime) -> float:
        result = self.db_connection.execute('SELECT SUM(strftime(\'%s\', end) - strftime(\'%s\', start))/3600.0 '
                                            'FROM shift '
                                            'WHERE entity_id=? '
                                            'AND start '
                                            'BETWEEN datetime(?) AND datetime(?);',
                                            (self.entity_id, start.isoformat(), end.isoformat())).fetchone()

        if result is None:
            return 0
        else:
            return result[0]

    def last_schedule_distance_hours(self, start: datetime, end: datetime) -> float:
        # Case one: there is overlap
        result = self.db_connection.execute('SELECT id FROM shift '
                                            'WHERE entity_id=? '
                                            'AND ((start BETWEEN datetime(?) AND datetime(?)) '
                                            'OR (end BETWEEN datetime(?) AND datetime(?)))',
                                            (self.entity_id, start.isoformat(), end.isoformat(),
                                             start.isoformat(), end.isoformat())).fetchall()
        if len(result) > 0:
            return 0

        # Case Two: no overlap, just find the min distance
        result = self.db_connection.execute('SELECT MIN(ABS(strftime(\'%s\', start) - strftime(\'%s\', ?))), '
                                            'MIN(ABS(strftime(\'%s\', end) - strftime(\'%s\', ?))) '
                                            'FROM shift '
                                            'WHERE entity_id=?',
                                            (start.isoformat(), end.isoformat(), self.entity_id)).fetchone()
        if result is None:
            return -1
        else:
            return min(result[0], result[1])
