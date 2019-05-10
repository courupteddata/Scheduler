from flask import request, jsonify, Blueprint, abort

from scheduler import entitymanager


entity_api = Blueprint('entity_api', __name__)

shared_entity_manager = entitymanager.EntityManager()


@entity_api.route("/entity", methods=['GET'])
def entity_get():
    return jsonify({'entity': shared_entity_manager.get_entity()})


@entity_api.route("/entity", methods=['POST'])
def entity_post():
    data = request.get_json()

    if data is None or "name" not in data:
        abort(400)

    entity = {"entity_id": shared_entity_manager.create_entity(data["name"])}

    return jsonify(entity)

