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

    entityapi.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from flask import request, jsonify, Blueprint
from dateutil import parser
from scheduler import entitymanager, entityrequirement, requirementhelper

entity_api = Blueprint('entity_api', __name__)

shared_entity_manager = entitymanager.EntityManager()


@entity_api.route("/entity", methods=['GET'])
def entity_get():
    return jsonify({'entity': shared_entity_manager.get_entity()})


@entity_api.route("/entity", methods=['POST'])
def entity_post():
    data = request.get_json(silent=True)

    if data is None or "entity_name" not in data:
        return jsonify({"error": "entity_name not found in body data"}), 400

    return jsonify({"entity_id": shared_entity_manager.create_entity(data["entity_name"])})


@entity_api.route("/entity/<int:entity_id>", methods=['GET'])
def entity_id_get(entity_id: int):
    entity = shared_entity_manager.get_entity_by_id(entity_id)

    if entity is None:
        return jsonify({"error": "entity_id not found"}), 400

    to_return = {"entity_requirement": [], "entity_name": entity.name, "entity_id": entity.entity_id}

    for req in entity.requirements:
        to_return["entity_requirement"].append(req.serialize())

    return jsonify(to_return)


@entity_api.route("/entity/<int:entity_id>/stats", methods=['GET'])
def entity_id_get_stats(entity_id: int):
    start = request.args.get('start', type=str, default=None)
    end = request.args.get('end', type=str, default=None)

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

    return jsonify({"entity_id": entity_id, "stats": shared_entity_manager.get_stats_for_entity(entity_id, start, end)})


@entity_api.route("/entity/<int:entity_id>", methods=['PUT'])
def entity_id_put(entity_id: int):
    data = request.get_json(silent=True)

    if data is None or "entity_name" not in data:
        return jsonify({"error": "entity_name not found in body data"}), 400

    if shared_entity_manager.update_entity_name(entity_id, data["entity_name"]) == 0:
        return jsonify({"error": "entity_id not found and name not updated"}), 400

    return jsonify({"entity_id": entity_id})


@entity_api.route("/entity/<int:entity_id>", methods=['DELETE'])
def entity_id_delete(entity_id: int):
    if not shared_entity_manager.delete_entity(entity_id):
        return jsonify({"error": "entity_id not found"}), 400

    return jsonify({"items_deleted": 1})


@entity_api.route("/entity/<int:entity_id>/requirement", methods=['GET'])
def entity_requirement_get(entity_id: int):
    data = shared_entity_manager.get_requirements_for_entity(entity_id)

    return jsonify({"requirement": [{"requirement_id": entry[0],
                                     "requirement_type": entry[1],
                                     "requirement_data": entry[2].serialize()} for entry in data]})


@entity_api.route("/entity/<int:entity_id>/requirement", methods=['POST'])
def entity_requirement_post(entity_id: int):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "json body data not found"}), 400

    req_types = [requirementhelper.RequirementType.RELATIVE.name,
                 requirementhelper.RequirementType.BASE.name,
                 requirementhelper.RequirementType.TIMEFRAME.name,
                 requirementhelper.RequirementType.TOTALS.name]

    if "requirement_type" not in data or data["requirement_type"] not in req_types:
        return jsonify({"error": f"requirement_type is missing or invalid, valid types are {req_types}"}), 400

    if "data" not in data:
        return jsonify({"error": "missing data field"}), 400

    if shared_entity_manager.get_entity_by_id(entity_id, False) is None:
        return jsonify({"error": "entity_id is invalid"}), 400

    if "cost" not in data["data"]:
        return jsonify({"error": "missing cost field"}), 400
    cost = data["data"]["cost"]

    if "label" not in data["data"]:
        return jsonify({"error": "missing label field"}), 400
    label = data["data"]["label"]

    if data["requirement_type"] == requirementhelper.RequirementType.BASE.name:
        requirement = entityrequirement.EntityRequirement(cost, label)
    elif data["requirement_type"] == requirementhelper.RequirementType.TIMEFRAME.name:
        time_frame_types = [entityrequirement.TimeFrameRequirement.Types.DATE_RANGE.name,
                            entityrequirement.TimeFrameRequirement.Types.DAY_OF_WEEK.name,
                            entityrequirement.TimeFrameRequirement.Types.TIME_RANGE.name]

        if "time_frame_type" not in data["data"] or data["data"]["time_frame_type"] not in time_frame_types:
            return jsonify({"error": f"missing or invalid time_frame_type field, like: {time_frame_types}"}), 400
        time_frame_type = data["data"]["time_frame_type"]

        if time_frame_type == entityrequirement.TimeFrameRequirement.Types.DAY_OF_WEEK.name:
            if "day_of_week" not in data["data"]:
                return jsonify({"error": "Missing day_of_week that is between 0-6 to represent Monday to Sunday"}), 400
        elif time_frame_type == entityrequirement.TimeFrameRequirement.Types.DATE_RANGE.name:
            if "datetime_start" not in data["data"] or "datetime_end" not in data["data"]:
                return jsonify({"error": "Missing datetime_start or datetime_end that should be IOS8601 format"}), 400
        elif time_frame_type == entityrequirement.TimeFrameRequirement.Types.TIME_RANGE.name:
            if "time_start" not in data["data"] or "time_end" not in data["data"]:
                return jsonify({"error": "Missing time_start or time_end that should be IOS8601 format HH:MM:SS"}), 400
        try:
            requirement = entityrequirement.TimeFrameRequirement.unserialize(data["data"])
        except Exception as e:
            return jsonify({"error": f"failed to parse. {str(e)}"}), 400
    elif data["requirement_type"] == requirementhelper.RequirementType.RELATIVE.name:
        if "during" not in data["data"] and "after" not in data["data"]:
            return jsonify({"error": "Missing during and after boolean flag (pick one to be true)"}), 400
        if "distance" not in data["data"] or not isinstance(data["data"]["distance"], (int, float)):
            return jsonify({"error": "Missing distance in hours (float) or invalid data passed"}), 400
        during = data["data"]["during"]
        after = data["data"]["after"]
        if (during and after) or (not during and not after):
            return jsonify({"error": "Only one of the two flags, during and after, should be true"}), 400
        try:
            requirement = entityrequirement.RelativeRequirement.unserialize(data["data"])
        except Exception as e:
            return jsonify({"error": f"failed to parse. {str(e)}"}), 400
    else:  # It must be a totals requirement
        error_message = ""
        if "total_requirement" not in data["data"]:
            error_message += "Missing total_requirement (float, hours). "
        if "is_rolling" not in data["data"]:
            error_message += "Missing is_rolling (boolean). "
        if "scale" not in data["data"]:
            error_message += "Missing scale (boolean). "
        if "start" not in data["data"]:
            error_message += "Missing start (ISO8601 datetime format) "

        if error_message != "":
            return jsonify({"error": error_message}), 400

        if "length" not in data["data"] and data["data"]["is_rolling"]:
            error_message += "Missing length (float, hours) "
        else:
            data["data"]["length"] = 0

        if "end" not in data["data"] and not data["data"]["is_rolling"]:
            error_message += "Missing end (ISO8601 datetime format)"
        else:
            data["data"]["end"] = "0001-01-01T00:00:00"

        if error_message != "":
            return jsonify({"error": error_message}), 400
        try:
            requirement = entityrequirement.TotalsRequirement.unserialize(data["data"])
        except Exception as e:
            return jsonify({"error": f"failed to parse. {str(e)}"}), 400

    return jsonify({"requirement_id": shared_entity_manager.add_requirement_to_entity(entity_id, requirement)})


@entity_api.route("/entity/<int:entity_id>/requirement/<int:requirement_id>", methods=['GET', 'DELETE'])
def entity_requirement_id_get_delete(entity_id: int, requirement_id: int):
    if request.method == 'GET':
        data = shared_entity_manager.get_requirement_id(requirement_id)
        if data is None:
            return jsonify({"error": "Unable to find requirement"}), 400
        return jsonify({"requirement_id": requirement_id,
                        "requirement_type": data[0],
                        "requirement_data": data[1].serialize()})
    else:
        return jsonify({"items_deleted": shared_entity_manager.delete_requirement(requirement_id)})


@entity_api.route("/entity/requirement/<int:requirement_id>", methods=['GET', 'DELETE'])
def entity_requirement_id_get_delete_no_ent(requirement_id: int):
    return entity_requirement_id_get_delete(0, requirement_id)


@entity_api.route("/entity/<int:entity_id>/location", methods=['GET'])
def entity_get_location(entity_id: int):
    return jsonify({"location": shared_entity_manager.get_location_for_entity(entity_id)})
