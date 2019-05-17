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

    schedulerapi.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from flask import jsonify, Blueprint

from scheduler import scheduler

scheduler_api = Blueprint('scheduler_api', __name__)

shared_scheduler = scheduler.Scheduler()


@scheduler_api.route("/scheduler/fill", methods=['POST'])
def scheduler_fill_all():
    data = shared_scheduler.fill_schedules_on_separate_thread()

    return jsonify({"scheduling": [{"work_id": item[0], "location_id": item[1]} for item in data]})


@scheduler_api.route("/scheduler/<int:location_id>", methods=['POST'])
def scheduler_fill_individual(location_id: int):
    if not shared_scheduler.shift_manager.validate_location_id(location_id):
        return jsonify({"error": "Invalid location id."}), 400

    data = shared_scheduler.fill_schedule_on_separate_thread(location_id)
    return jsonify({"scheduling": {"work_id": data, "location_id": location_id}})
