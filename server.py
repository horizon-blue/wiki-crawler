from flask import Flask
from flask_restful import Api
from database import db_session
from api import *

app = Flask(__name__)
api = Api(app)

api.add_resource(ActorResource, '/actors')


@app.teardown_appcontext
def shutdown_session(_=None):
    """
    Close db_session when closing the server
    """
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=True)
