from flask import Flask
from flask_restful import Resource, Api
from database import db_session
from model.graph import Graph

app = Flask(__name__)
api = Api(app)
graph = Graph(db_session)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/')


@app.teardown_appcontext
def shutdown_session(_=None):
    """
    Close db_session when closing the server
    """
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=True)
