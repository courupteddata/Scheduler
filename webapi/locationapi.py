from flask import request, jsonify, Blueprint

from scheduler import locationmanager

location_api = Blueprint('location_api', __name__)

shared_location_manager = locationmanager.LocationManager()


@location_api.route("/location", methods=['GET'])
def location_get():
    return jsonify({"location": [{"location_id": loc.location_id, "location_label": loc.label}
                                 for loc in shared_location_manager.get_locations()]})


@location_api.route("/location", methods=['POST'])
def location_post():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Missing body data"}), 400
    if "location_label" not in data:
        return jsonify({"error": "Missing location_label"}), 400

    return jsonify({"location_id": shared_location_manager.create_location(data["location_label"])})


@location_api.route("/location/<int:location_id>", methods=['PUT'])
def location_put(location_id: int):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Missing body data"}), 400

    if "location_label" not in data:
        return jsonify({"error": "location_label is missing."}), 400

    return jsonify({"location_updated":
                    shared_location_manager.update_location(location_id, data["location_label"])})


@location_api.route("/location/<int:location_id>/entity", methods=['GET'])
def location_get_entity_id(location_id: int):
    return jsonify({"entity_ids": shared_location_manager.get_entity_ids_by_location_id(location_id)})


@location_api.route("/location/<int:location_id>/entity/<int:entity_id>", methods=['PUT', 'DELETE'])
def location_update_entity(location_id: int, entity_id: int):
    if request.method == 'PUT':
        return jsonify({"location_added": shared_location_manager.add_location_to_entity(location_id, entity_id) == 1})
    else:
        return jsonify({"location_deleted": shared_location_manager.
                       remove_location_from_entity(location_id, entity_id) == 1})


@location_api.route("/location/<int:location_id>", methods=['DELETE'])
def location_delete(location_id: int):
    return jsonify({"location_deleted": shared_location_manager.delete_location(location_id)})
