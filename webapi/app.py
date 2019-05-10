from flask import Flask
from webapi import entityapi

app = Flask(__name__)
API_PREFIX = "/api/v1"
app.register_blueprint(entityapi.entity_api, url_prefix=API_PREFIX)

# look into https://www.getpostman.com/postman
@app.before_first_request
def prepare_api():
    """
    Called to prepare the API with local storage
    :return:
    """
    pass


if __name__ == '__main__':
    app.run(debug=True)
