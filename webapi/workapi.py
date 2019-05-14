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

    workapi.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from flask import request, jsonify, Blueprint

from scheduler import workmanager

work_api = Blueprint('work_manager_api', __name__)

shared_work_manager = workmanager.WorkManager()


@work_api.route("/work", methods=['GET'])
def work_get():
    data = shared_work_manager.get_all_work()

    return jsonify({"work": [{"work_id": item[0], "work_progress": item[1], "work_message": item[2]} for item in data]})


@work_api.route("/work", methods=['DELETE'])
def work_delete_all():
    return jsonify({"work_deleted": shared_work_manager.delete_all_entry()})


@work_api.route("/work/<int:work_id>", methods=['DELETE', 'GET'])
def work_delete_get_single(work_id: int):
    if request.method == 'DELETE':
        return jsonify({"work_deleted": shared_work_manager.delete_single_entry(work_id)})
    else:
        data = shared_work_manager.get_single_work(work_id)
        if data is None:
            return jsonify({"error": "shift_id not found"}), 400
        else:
            return jsonify({"work": data})
