from flask import request, jsonify, Blueprint

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

    return jsonify({})


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

    req_types = [req_type.Name for req_type in requirementhelper.RequirementType]

    if "requirement_type" not in data or data["requirement_type"] not in req_types:
        return jsonify({"error": f"requirement_type is missing or invalid, valid types are {req_types}"}), 400

    return ""
