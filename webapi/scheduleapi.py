from flask import request, jsonify, Flask, Blueprint, abort
from scheduler import schedule
from dateutil import parser


schedule_api = Blueprint('schedule_api', __name__)


@schedule_api.route("/schedule/template/", methods=["POST"])
def create_schedule_from_template():
    """
    Expects data of format:
    {
    end: "ISO8601 format",
    week: [
            [{start: "ISO8601 format", end: "ISO8601 format", label: ""}, ...],
            [{start: "ISO8601 format", end: "ISO8601 format", label: ""}, ...],
            ...
          ]
    }

    :return:
    """
    data = request.get_json()

    if data is None or data["end"] is None or data["week"] is None:
        abort(400)  # Need data with the post, otherwise error out

    template = []
    index = 0
    for day in data:
        template.append([])
        for entry in day:
            template[index].append(schedule.Shift(parser.parse(entry["start"]),
                                                  parser.parse(entry["end"]),
                                                  entry.get("label", "")))
        index += 1

    return {
        "response": schedule.Schedule.create_template_from_sample(end=parser.parse(data["end"]), week=template).to_json(),
        "status": 200,
        "mimetype": "application/json"
        }



