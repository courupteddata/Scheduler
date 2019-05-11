from flask import request, jsonify, Blueprint
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

    return jsonify({"shift": [item.serialize() for item in
                              shared_shift_manager.get_shift_by_location_id(location_id, start, end, entity_id)]})


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
        if not shared_shift_manager.validate_entity_id(data["entity_id"]):
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

    try:
        converted_data = []
        for item in data['sample']:

            if not isinstance(item, list):
                return jsonify({"error": "Sample should contain lists of lists"}), 400
            converted_data.append([shiftmanager.Shift.unserialize(thing) for thing in item])
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
