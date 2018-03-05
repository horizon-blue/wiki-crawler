from flask import Flask
from flask_restful import Api
from database import db_session
from api import *

app = Flask(__name__)
api = Api(app)

API_ROOT = '/api'

api.add_resource(ActorQueryResource, API_ROOT + '/actors')
api.add_resource(ActorResource, API_ROOT + '/actors/<string:name>')
api.add_resource(MovieQueryResource, API_ROOT + '/movies')
api.add_resource(MovieResource, API_ROOT + '/movies/<string:name>')


@app.teardown_appcontext
def shutdown_session(_=None):
    """
    Close db_session when closing the server
    """
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=True)
