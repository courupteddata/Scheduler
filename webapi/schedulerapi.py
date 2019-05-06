from flask import request, jsonify, Flask, Blueprint
from typing import TYPE_CHECKING
from os import path
import os
import pickle

from scheduler import scheduler

if TYPE_CHECKING:
    from scheduler import entitymanager

FLAT_FILE_NAME = "storage.pickle"

scheduler_api = Blueprint('scheduler_api', __name__)
shared_scheduler = scheduler.Scheduler()


def prepare():
    global shared_entity_manager
    if path.exists(FLAT_FILE_NAME):
        os.remove(FLAT_FILE_NAME)
        with open(FLAT_FILE_NAME, "rb") as f:
            shared_entity_manager: scheduler.Scheduler = pickle.load(f)

        try:
            os.remove(FLAT_FILE_NAME + ".backup")
        except OSError:
            pass

        with open(FLAT_FILE_NAME + ".backup", "wb") as f:
            pickle.dump(shared_entity_manager, f)
