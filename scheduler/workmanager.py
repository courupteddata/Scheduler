from typing import Tuple, List
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

    def delete_all_entry(self) -> int:
        modified_rows = self.connection.execute("DELETE FROM work;").rowcount
        self.connection.commit()

        return modified_rows

    def delete_single_entry(self, work_id: int) -> int:
        modified_rows = self.connection.execute("DELETE FROM work WHERE id=?", (work_id,)).rowcount
        self.connection.commit()
        return modified_rows
