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

    shiftapi.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from flask import request, jsonify, Blueprint, make_response
from dateutil import parser
from datetime import timedelta
from scheduler import shiftmanager

shift_api = Blueprint('shift_api', __name__)

shared_shift_manager = shiftmanager.ShiftManager()


@shift_api.route("/shift", methods=['GET'])
def shift_get():
    location_id = request.args.get('location_id', type=int, default=-1)
    start = request.args.get('start', type=str, default=None)
    end = request.args.get('end', type=str, default=None)
    entity_id = request.args.get('entity_id', type=int, default=-2)
    export = request.args.get('export', type=bool, default=False)

    if start is not None:
        try:
            start = parser.parse(start)
        except Exception as e:
            return jsonify({"error": f"invalid start. {str(e)}"}), 400

    if end is not None:
        try:
            end = parser.parse(end)
        except Exception as e:
            return jsonify({"error": f"invalid end. {str(e)}"}), 400

    if not export:
        return jsonify({"shift": [item.serialize() for item in
                       shared_shift_manager.get_shift_by_location_id(location_id, start, end, entity_id)]})

    data = "\"Subject\",\"Start Date\",\"Start Time\",\"End Date\",\"End Time\",\"Description\",\"Location\"\r\n"
    shifts = shared_shift_manager.get_shift_by_location_id(location_id, start, end, entity_id)

    empty = "Empty"

    for shift in shifts:
        start_time = shift.start.time().strftime("%I:%M %p")
        start_date = shift.start.date().strftime("%m/%d/%Y")

        end_time = shift.end.time().strftime("%I:%M %p")
        end_date = shift.end.date().strftime("%m/%d/%Y")

        data += f"\"{shared_shift_manager.get_entity_name(shift.entity_id) if shift.entity_id != -1 else empty}\"," \
            f"\"{start_date}\",\"{start_time}\",\"{end_date}\",\"{end_time}\",\"{shift.info}\"," \
            f"\"{shared_shift_manager.get_location_label(shift.location_id)}\"\r\n"

    output = make_response(data)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-Type"] = "text/csv"
    return output


@shift_api.route("/shift", methods=['POST'])
def shift_add():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Missing body data"}), 400

    error_msg = ""

    if "start" not in data:
        error_msg += "start field missing (ISO8601 datetime). "
    if "end" not in data:
        error_msg += "end field missing (ISO8601 datetime). "
    if "location_id" not in data:
        error_msg += "location_id field missing (integer). "
    else:
        if not shared_shift_manager.validate_location_id(data["location_id"]):
            error_msg += "invalid location_id.  "

    if "info" not in data:
        data["info"] = ""

    if "entity_id" not in data:
        data["entity_id"] = -1
    else:
        if data["entity_id"] != -1 and not shared_shift_manager.validate_entity_id(data["entity_id"]):
            error_msg += "invalid entity_id.  "

    if error_msg != "":
        return jsonify({"error": error_msg}), 400

    data["shift_id"] = -1

    try:
        shift = shiftmanager.Shift.unserialize(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"shift_id": shared_shift_manager.add_shift(shift)})


@shift_api.route("shift/template", methods=['POST'])
def shift_add_template():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Missing body data"}), 400

    if "sample" not in data:
        return jsonify({"error": "Missing sample attribute"}), 400

    if "end" not in data:
        return jsonify({"error": "Missing end attribute (ISO8601 datetime)"}), 400

    try:
        end = parser.parse(data["end"])
    except Exception as e:
        return jsonify({"error": f"invalid end. {str(e)}"}), 400

    list_flag = False
    dict_flag = False

    try:
        converted_data = []
        for item in data['sample']:

            if isinstance(item, list):
                converted_data.append([shiftmanager.Shift.unserialize(thing) for thing in item])
                list_flag = True

            if isinstance(item, dict):
                converted_data.append(shiftmanager.Shift.unserialize(item))
                dict_flag = True

            if list_flag and not isinstance(item, list):
                return jsonify({"error": "Sample found a dict when expecting list of list of shifts"}), 400

            if dict_flag and not isinstance(item, dict):
                return jsonify({"error": "Sample found a list when expecting list of shifts"}), 400

    except Exception as e:
        return jsonify({"error": f"Error parsing sample. {str(e)}"}), 400

    return jsonify({"shifts_added": shared_shift_manager.add_shift_from_sample(converted_data, end)})


@shift_api.route("shift/repeat", methods=['POST'])
def shift_add_repeat():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Missing body data"}), 400

    error_msg = ""
    if "shift_length" not in data:
        error_msg += "Missing shift_length attribute (float, hours).  "
    if "start" not in data:
        error_msg += "Missing start attribute (ISO8601 datetime).  "
    if "end" not in data:
        error_msg += "Missing end attribute (ISO8601 datetime).  "
    if "location_id" not in data:
        error_msg += "Missing location_id attribute"
    else:
        if not shared_shift_manager.validate_location_id(data["location_id"]):
            error_msg += "Invalid location_id.  "
    if "info" not in data:
        data["info"] = ""

    if error_msg != "":
        return jsonify({"error": error_msg}), 400

    try:
        end = parser.parse(data["end"])
    except Exception as e:
        return jsonify({"error": f"invalid end. {str(e)}"}), 400

    try:
        start = parser.parse(data["start"])
    except Exception as e:
        return jsonify({"error": f"invalid start. {str(e)}"}), 400

    return jsonify({"shifts_added": shared_shift_manager.add_from_shift_length(
        timedelta(hours=data["shift_length"]), start, end, data["location_id"], data["info"])})


@shift_api.route("/shift/<int:shift_id>", methods=['DELETE'])
def shift_delete(shift_id: int):
    return jsonify({"shift_deleted": shared_shift_manager.delete_shift(shift_id) > 0})


@shift_api.route("/shift/<int:shift_id>", methods=['PUT'])
def shift_put(shift_id: int):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Missing body data"}), 400

    error_msg = ""

    start = None
    end = None
    location_id = None
    info = None
    entity_id = None

    if "start" in data:
        try:
            start = parser.parse(data["start"])
        except Exception as e:
            error_msg += f"invalid start. {str(e)}"
    if "end" not in data:
        try:
            end = parser.parse(data["end"])
        except Exception as e:
            error_msg += f"invalid end. {str(e)}"

    if "location_id" in data:
        if not shared_shift_manager.validate_location_id(data["location_id"]):
            error_msg += "invalid location_id.  "
        else:
            location_id = data["location_id"]

    if "info" in data:
        info = data["info"]

    if "entity_id" in data:
        if data["entity_id"] != -1 and not shared_shift_manager.validate_entity_id(data["entity_id"]):
            error_msg += "invalid entity_id.  "
        else:
            entity_id = data["entity_id"]

    if start is not None and end is not None:
        if start > end:
            error_msg += "start must be before end.  "

    if error_msg != "":
        return jsonify({"error": error_msg}), 400

    shift = shared_shift_manager.update_parts_of_shift(shift_id, start, end, location_id, info, entity_id)

    if shift is None:
        return jsonify({"error": "Could not find shift id or you did not pass any information to update"}), 400

    return jsonify({"shift": shift.serialize()})


@shift_api.route("/shift/<int:shift_id>", methods=['GET'])
def shift_get_by_id(shift_id: int):
    data = shared_shift_manager.get_shift_by_id(shift_id)

    if data is None:
        return jsonify({"error": "Shift now found"}), 400

    return jsonify({"shift": data.serialize()})
