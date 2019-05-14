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

    workmanager.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from typing import Tuple, List, Union, Dict
from . import shared


class WorkManager:

    def __init__(self):
        self.connection = shared.DB().get_connection()
        shared.DB.create_all_tables()

    def add_work_entry(self, msg: str) -> int:
        rowid = self.connection.execute("INSERT INTO work(progress,message) VALUES (?,?);", (0, msg)).lastrowid
        self.connection.commit()

        return rowid

    def update_work_entry(self, work_id: int, progress: float, msg: str):
        self.connection.execute("UPDATE work SET progress=?,message=? WHERE id=?;", (progress, msg, work_id))
        self.connection.commit()

    def get_all_work(self) -> List[Tuple[int, float, str]]:
        data = self.connection.execute("SELECT id, progress, message FROM work;").fetchall()

        if data is None or len(data) == 0:
            return []

        return [(entry[0], entry[1], entry[2]) for entry in data]

    def get_single_work(self, work_id: int) -> Union[None, Dict]:
        data = self.connection.execute("SELECT id, progress, message FROM work WHERE id=?", (work_id,)).fetchone()

        if data is None:
            return None
        return {"work_id": data[0], "work_progress": data[1], "work_message": data[2]}

    def delete_all_entry(self) -> int:
        modified_rows = self.connection.execute("DELETE FROM work;").rowcount
        self.connection.commit()

        return modified_rows

    def delete_single_entry(self, work_id: int) -> int:
        modified_rows = self.connection.execute("DELETE FROM work WHERE id=?", (work_id,)).rowcount
        self.connection.commit()
        return modified_rows
