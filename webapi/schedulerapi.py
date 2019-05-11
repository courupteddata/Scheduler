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
