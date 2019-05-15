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

    shiftmanager.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from datetime import datetime, timedelta
from typing import List, Dict, Union
import math
from dateutil import parser
import copy
from threading import Lock

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

        if "info" not in data:
            data["info"] = ""

        if "entity_id" not in data:
            data["entity_id"] = -1

        if "shift_id" not in data:
            data["shift_id"] = -1

        return Shift(start, end, data["location_id"],
                     data["info"], data["entity_id"], data["shift_id"])


class ShiftManager:
    def __init__(self):
        shared.DB.create_all_tables()
        self.connection = shared.DB().get_connection()
        self.connection_modify_lock = Lock()

    def add_shift(self, shift: Shift) -> int:
        with self.connection_modify_lock:
            last_row_id = self.connection.execute("INSERT INTO shift(start, end, info, entity_id, location_id) "
                                                  "VALUES (?,?,?,?,?)",
                                                  (shift.start.isoformat(), shift.end.isoformat(),
                                                   shift.info, shift.entity_id, shift.location_id)).lastrowid
            self.connection.commit()
        return last_row_id

    def delete_shift(self, shift_id: int) -> int:
        with self.connection_modify_lock:
            modified_row_count = self.connection.execute("DELETE FROM shift WHERE id=?", (shift_id,)).rowcount
            self.connection.commit()

        return modified_row_count

    def update_shift(self, shift: Shift) -> int:
        with self.connection_modify_lock:
            modified_row_count = self.connection.execute("UPDATE shift SET start=?,end=?,info=?,entity_id=?,"
                                                         "location_id=? WHERE id=?",
                                                         (shift.start.isoformat(), shift.end.isoformat(), shift.info,
                                                          shift.entity_id, shift.location_id)).rowcount
            self.connection.commit()
        return modified_row_count

    def get_shift_by_id(self, shift_id: int) -> Union[None, Shift]:
        data = self.connection.execute("SELECT id, start, end, info, entity_id, location_id FROM shift WHERE id=?;",
                                       (shift_id,)).fetchone()

        if data is None:
            return None

        return Shift(shift_id=data[0], start=parser.parse(data[1]), end=parser.parse(data[2]), info=data[3],
                     entity_id=data[4], location_id=data[5])

    def update_parts_of_shift(self, shift_id: int, start: datetime = None, end: datetime = None,
                              location_id: int = None, info: str = None, entity_id: int = None) -> Union[None, Shift]:
        if self.get_shift_by_id(shift_id) is None:
            return None

        set_string = ""
        query_params = ()
        previous = False

        if start is not None:
            previous = True
            query_params += (start.isoformat(),)
            set_string += "start=?"
        if end is not None:
            if previous:
                set_string += ","
            previous = True
            query_params += (end.isoformat(),)
            set_string += "end=?"
        if location_id is not None:
            if previous:
                set_string += ","
            previous = True
            query_params += (location_id,)
            set_string += "location_id=?"
        if info is not None:
            if previous:
                set_string += ","
            previous = True
            query_params += (info,)
            set_string += "info=?"

        if entity_id is not None:
            if previous:
                set_string += ","
            previous = True
            query_params += (entity_id,)
            set_string += "entity_id=?"

        if previous:
            set_string = " SET " + set_string
            query_params += (shift_id,)

            with self.connection_modify_lock:
                self.connection.execute(f"UPDATE shift {set_string} WHERE id=?;", query_params)
                self.connection.commit()

            return self.get_shift_by_id(shift_id)

        return None

    def fill_shift_by_id(self, shift_id: int, entity_id: int) -> int:
        with self.connection_modify_lock:
            modified_row_count = self.connection.execute("UPDATE shift SET entity_id=? WHERE id=?",
                                                         (entity_id, shift_id)).rowcount
            self.connection.commit()
        return modified_row_count

    def get_shift_by_location_id(self, location_id: int = -1,
                                 start: datetime = None, end: datetime = None, entity_id: int = -2) -> List[Shift]:

        where_query_string = ""
        query_data = ()
        previous = False

        if location_id != -1:
            previous = True
            where_query_string += " location_id=?"
            query_data += (location_id,)

        if entity_id != -2:
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

    def add_shift_from_sample(self, template_week: Union[List[Shift], List[List[Shift]]], end: datetime) -> int:

        if len(template_week) == 0:
            return -1

        if isinstance(template_week[0], Shift):
            template_week.sort()
            week = [[]]
            index = 0
            current_date = template_week[0].start.date()
            for entry in template_week:
                if entry.start.date() == current_date:
                    week[index].append(copy.deepcopy(entry))
                else:
                    week.append([copy.deepcopy(entry)])
                    current_date = entry.start.date()
                    index += 1
        elif isinstance(template_week, list):
            week = template_week
            for day in week:
                day.sort()
        else:
            return -1

        shifts = []
        start = week[0][0].start
        end = week[0][0].end

        # Put the template in the shift list
        for day in week:
            for shift in day:
                if shift.entity_id != -1:
                    if not self.validate_entity_id(shift.entity_id):
                        return -1
                if not self.validate_location_id(shift.location_id):
                    return -1

                if shift.end > end:
                    end = shift.end

                shifts.append(copy.deepcopy(shift))

        """
        |M|T|W|T|F|S|S|
        |M|T|W|T|F|S|S|
        |M|T|W|T|F|S|S|
        """
        length = (end - start).total_seconds()
        seconds_in_a_week = 604800
        week_offset = length / seconds_in_a_week
        days_offset = math.ceil(week_offset) * 7

        shift_offset_increment = timedelta(days=days_offset)
        shift_offset = shift_offset_increment

        working = True

        while working:
            for day in week:
                for shift in day:
                    if shift.end + shift_offset > end:
                        working = False
                        break
                    a_copy = copy.deepcopy(shift)
                    a_copy.start += shift_offset
                    a_copy.end += shift_offset
                    shifts.append(a_copy)
            shift_offset = shift_offset + shift_offset_increment
        count = 0

        with self.connection_modify_lock:
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

        with self.connection_modify_lock:
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
                                                    "FROM shift WHERE location_id=? AND entity_id=-1;",
                                                    (location_id,))]

    def validate_location_id(self, location_id: int) -> bool:
        return self.connection.execute("SELECT id FROM location WHERE id=?;", (location_id,)).fetchone() is not None

    def validate_entity_id(self, entity_id: int) -> bool:
        return self.connection.execute("SELECT id FROM entity WHERE id=?;", (entity_id,)).fetchone() is not None

    def get_location_label(self, location_id: int) -> str:
        data = self.connection.execute("SELECT label FROM location WHERE id=?;", (location_id,)).fetchone()
        if data is None:
            return ""
        return data[0]

    def get_entity_name(self, entity_id: int) -> str:
        data = self.connection.execute("SELECT name FROM entity WHERE id=?;", (entity_id,)).fetchone()
        if data is None:
            return ""
        return data[0]
