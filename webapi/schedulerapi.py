import flask
from flask import request, jsonify

from scheduler import scheduler

app = flask.Flask(__name__)

"""
Example for something to run before 
@app.before_first_request
def activate_job():
    def run_job():
        while True:
            print("Run recurring task")
            time.sleep(3)

    thread = threading.Thread(target=run_job)
    thread.start()
"""


if __name__ == '__main__':
    app.run(debug=True)