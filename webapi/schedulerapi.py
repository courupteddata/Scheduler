from flask import request, jsonify, Flask, Blueprint

from scheduler import scheduler

scheduler_api = Blueprint('scheduler_api', __name__)
shared_scheduler: scheduler.Scheduler = scheduler.Scheduler()



