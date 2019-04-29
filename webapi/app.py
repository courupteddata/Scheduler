from flask import Flask
from . import schedulerapi

app = Flask(__name__)
API_PREFIX = "/api/v1"
app.register_blueprint(schedulerapi.scheduler_api, url_prefix=API_PREFIX)


@app.before_first_request
def prepare_api():
    """
    Called to prepare the API with local storage
    :return:
    """
    schedulerapi.prepare()


if __name__ == '__main__':
    app.run(debug=True)
