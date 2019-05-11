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
