from datetime import datetime, timedelta
from typing import List, Dict
import math
from dateutil import parser
import copy

from . import shared

#  Model everything as a list of shifts that can be on or off.


class Shift:

    def __init__(self, start: datetime, end: datetime, location_id: int,
                 info: str = "",
                 entity_id: int = -1,
                 shift_id: int = -1):
        self.shift_id = shift_id
        self.start = start
        self.end = end
        self.location_id = location_id
        self.info = info
        self.entity_id = entity_id

    def __lt__(self, other) -> bool:
        return self.start < other.start

    def serialize(self) -> Dict:
        return {"shift_id": self.shift_id,
                "start": self.start.isoformat(),
                "end": self.end.isoformat(),
                "location_id": self.location_id,
                "info": self.info,
                "entity_id": self.entity_id}

    @classmethod
    def unserialize(cls, data: Dict):
        start = parser.parse(data["start"])
        end = parser.parse(data["end"])

        if end < start:
            raise Exception("Invalid order, end should be after start")

        return Shift(start, end, data["location_id"],
                     data["info"], data["entity_id"], data["shift_id"])


class ShiftManager:
    def __init__(self):
        shared.DB.create_all_tables()
        self.connection = shared.DB().get_connection()

    def add_shift(self, shift: Shift) -> int:
        last_row_id = self.connection.execute("INSERT INTO shift(start, end, info, entity_id, location_id) "
                                              "VALUES (?,?,?,?,?)",
                                              (shift.start.isoformat(), shift.end.isoformat(),
                                               shift.info, shift.entity_id, shift.location_id)).lastrowid
        self.connection.commit()
        return last_row_id

    def delete_shift(self, shift_id: int) -> int:
        modified_row_count = self.connection.execute("DELETE FROM shift WHERE id=?", (shift_id,)).rowcount
        self.connection.commit()

        return modified_row_count

    def update_shift(self, shift: Shift) -> int:
        modified_row_count = self.connection.execute("UPDATE shift SET start=?,end=?,info=?,entity_id=?,location_id=? "
                                                     "WHERE id=?",
                                                     (shift.start.isoformat(), shift.end.isoformat(), shift.info,
                                                      shift.entity_id, shift.location_id)).rowcount
        self.connection.commit()
        return modified_row_count

    def fill_shift_by_id(self, shift_id: int, entity_id: int) -> int:
        modified_row_count = self.connection.execute("UPDATE shift SET entity_id=? WHERE id=?",
                                                     (entity_id, shift_id)).rowcount
        self.connection.commit()
        return modified_row_count

    def get_shift_by_location_id(self, location_id: int = -1,
                                 start: datetime = None, end: datetime = None, entity_id: int = -1) -> List[Shift]:

        where_query_string = ""
        query_data = ()
        previous = False

        if location_id != -1:
            previous = True
            where_query_string += " location_id=?"
            query_data += (location_id,)

        if entity_id != -1:
            if previous:
                where_query_string += " AND"
            previous = True
            where_query_string += " entity_id=?"
            query_data += (entity_id,)

        if start is not None:
            if previous:
                where_query_string += " AND"
            previous = True
            where_query_string += " start >= datetime(?)"
            query_data += (start.isoformat(),)

        if end is not None:
            if previous:
                where_query_string += " AND"
            where_query_string += " start <= datetime(?)"
            query_data += (end.isoformat(),)

        if where_query_string != "":
            where_query_string = " WHERE" + where_query_string

        return [Shift(shift_id=data[0], start=parser.parse(data[1]), end=parser.parse(data[2]), info=data[3],
                      entity_id=data[4], location_id=data[5]) for data in self.connection.execute(
            f"SELECT id, start, end, info, entity_id, location_id FROM shift {where_query_string};", query_data)]

    def get_shift_by_entity_id(self, entity_id: int) -> List[Shift]:
        return [Shift(shift_id=data[0], start=parser.parse(data[1]), end=parser.parse(data[2]),
                      info=data[3], entity_id=data[4], location_id=data[5])
                for data in self.connection.execute("SELECT id, start, end, info, entity_id, location_id "
                                                    "FROM shift WHERE entity_id=?", (entity_id,))]

    def add_shift_from_sample(self, week: List[List[Shift]], end: datetime) -> int:
        for day in week:
            day.sort()

        shifts = []
        start = week[0][0].start

        # Put the template in the shift list
        for day in week:
            for shift in day:
                if shift.entity_id != -1:
                    if not self.validate_entity_id(shift.entity_id):
                        return -1
                if not self.validate_location_id(shift.location_id):
                    return -1
                shifts.append(copy.deepcopy(shift))

        """
        |M|T|W|T|F|S|S|
        |M|T|W|T|F|S|S|
        |M|T|W|T|F|S|S|
        """
        length_of_week_list = len(week) - 1
        length_of_last_item = len(week[length_of_week_list]) - 1
        length = (week[length_of_week_list][length_of_last_item].end - start).total_seconds()
        seconds_in_a_week = 604800
        week_offset = length/seconds_in_a_week
        days_offset = math.ceil(week_offset) * 7

        shift_offset_increment = timedelta(days=days_offset)
        shift_offset = shift_offset_increment

        working = True

        while working:
            for day in week:
                for shift in day:
                    if shift.end+shift_offset > end:
                        working = False
                        break
                    a_copy = copy.deepcopy(shift)
                    a_copy.start += shift_offset
                    a_copy.end += shift_offset
                    shifts.append(a_copy)
            shift_offset = shift_offset + shift_offset_increment
        count = 0

        for shift in shifts:
            count += self.connection.execute("INSERT INTO shift(start, end, info, entity_id, location_id) "
                                             "VALUES (?,?,?,?,?)",
                                             (shift.start.isoformat(), shift.end.isoformat(), shift.info,
                                              shift.entity_id, shift.location_id)).rowcount
        self.connection.commit()

        return count

    def add_from_shift_length(self, shift_length: timedelta, start: datetime,
                              end: datetime, location_id: int, info: str = "") -> int:
        """
        Creates a blank calendar that can be scheduled into.
        :param shift_length: The number of hours that a shift should be
        :param start: The datetime to start
        :param end: The datetime to stop
        :param location_id: the location for these shifts
        :param info: information to be added to these shifts
        :return: a template that is ready to be filled
        """
        shifts = []

        current_datetime = start

        if not self.validate_location_id(location_id):
            return -1

        while current_datetime <= end:
            end_shift = current_datetime + shift_length

            shifts.append(Shift(start=current_datetime, end=end_shift, info=info, location_id=location_id))
            current_datetime = end_shift

        count = 0

        for shift in shifts:
            count += self.connection.execute("INSERT INTO shift(start, end, info, entity_id, location_id) "
                                             "VALUES (?,?,?,?,?)",
                                             (shift.start.isoformat(), shift.end.isoformat(), shift.info,
                                              shift.entity_id, shift.location_id)).rowcount
        self.connection.commit()

        return count

    def get_total_shift_count_by_location_id(self, location_id: int) -> int:
        count = self.connection.execute("SELECT COUNT(*) FROM shift WHERE location_id=?;", (location_id,)).fetchone()

        if count is None:
            return 0

        return count[0]

    def get_empty_shift_count_by_location_id(self, location_id: int) -> int:
        count = self.connection.execute("SELECT COUNT(*) FROM shift WHERE location_id=? "
                                        "AND entity_id=-1;", (location_id,)).fetchone()

        if count is None:
            return 0

        return count[0]

    def get_empty_shift_by_location_id(self, location_id: int) -> List[Shift]:
        return [Shift(shift_id=data[0], start=parser.parse(data[1]), end=parser.parse(data[2]),
                      info=data[3], entity_id=data[4], location_id=data[5])
                for data in self.connection.execute("SELECT id, start, end, info, entity_id, location_id "
                                                    "FROM shift WHERE location_id=? AND NOT entity_id=-1;",
                                                    (location_id,))]

    def validate_location_id(self, location_id: int) -> bool:
        return self.connection.execute("SELECT id FROM location WHERE id=?;", (location_id,)).fetchone() is not None

    def validate_entity_id(self, entity_id: int) -> bool:
        return self.connection.execute("SELECT id FROM entity WHERE id=?;", (entity_id,)).fetchone() is not None
