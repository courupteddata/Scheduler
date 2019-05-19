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

    app.py, Copyright 2019 Nathan Jones (Nathan@jones.one)
"""
from flask import Flask, send_from_directory
from webapi import entityapi, locationapi, shiftapi, schedulerapi, workapi
from threading import Lock
import webbrowser

app = Flask(__name__)
API_PREFIX = "/api/v1"
app.register_blueprint(entityapi.entity_api, url_prefix=API_PREFIX)
app.register_blueprint(locationapi.location_api, url_prefix=API_PREFIX)
app.register_blueprint(shiftapi.shift_api, url_prefix=API_PREFIX)
app.register_blueprint(schedulerapi.scheduler_api, url_prefix=API_PREFIX)
app.register_blueprint(workapi.work_api, url_prefix=API_PREFIX)

shared_lock = Lock()


@app.before_first_request
def prepare_api():
    """
    Called to prepare the API with a shared lock
    :return:
    """
    entityapi.shared_entity_manager.connection_modify_lock = shared_lock
    locationapi.shared_location_manager.connection_modify_lock = shared_lock
    shiftapi.shared_shift_manager.connection_modify_lock = shared_lock
    workapi.shared_work_manager.connection_modify_lock = shared_lock

    schedulerapi.shared_scheduler.set_lock(shared_lock)


@app.route("/<path:path>")
def get_static_page(path):
    return send_from_directory("UI", path)


@app.route("/")
def get_main_page():
    return send_from_directory("UI", "index.html")


if __name__ == '__main__':
    # In future add Threaded=True for possible performance enhancement
    webbrowser.open_new_tab("http://127.0.0.1:5000")
    print("Scheduler  Copyright (C) 2019  Nathan Jones (Nathan@jones.one)\n"
          "This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE file\n"
          "This is free software, and you are welcome to redistribute it\n"
          "under certain conditions, see LICENSE file.")
    app.run()

