from flask_restful import Resource, abort
from flask import request
from database import db_session
from sqlalchemy import and_, or_
from model.graph import Actor, Edge, Movie, Graph
from .util import parse_query

GROSS_RANGE = 5000
graph = Graph(db_session)


def generate_query(queries):
    """
    A helper method to get the actor query from queries
    :param queries: the list of dictionary containing queries to filter query
    :return: query corresponding to queries
    """
    filters = []
    for query in queries:
        query_filter = []
        # check each field
        if "name" in query:
            query_filter.append(Actor.name.contains(query.get("name")))
        if "age" in query:
            query_filter.append(Actor.age == int(query.get("age")))
        if "wiki_page" in query:
            query_filter.append(Actor.wiki_page.contains(query.get("name")))
        if "total_gross" in query:
            gross = float(query.get("total_gross"))
            query_filter.append(and_(Actor.total_gross >= gross - GROSS_RANGE,
                                     Actor.total_gross <= gross + GROSS_RANGE))
        if "movie" in query or "movies" in query:
            movie_list = [query.get("movie")] if "movie" in query else query.get("movies").split(',')
            query_filter.append(and_(*[Actor.movies.any(Edge.movie.has(Movie.name.contains(movie_name.strip())))
                                       for movie_name in movie_list]))
        filters.append(and_(*query_filter))
    return or_(*filters)


class ActorQueryResource(Resource):
    """
    The Flask-Restful Resource class used for creating
    API for Actor query
    Operates on: {API_ROOT}/actors
    """

    @staticmethod
    def get():
        try:
            queries = parse_query(request.query_string.decode("utf-8"))
            return [actor.to_dict() for actor in Actor.query.filter(generate_query(queries)).all()]
        except ValueError:
            abort(400, message="Cannot parse the query")

    @staticmethod
    def post():
        changes = request.get_json()
        if changes is None:
            abort(400, message="Incorrect mimetype or invalid json")
        else:
            graph.add_actor(changes, external=True)


class ActorResource(Resource):
    """
    The Flask-Restful Resource class used for creating
    API for a single Actor
    Operates on: {API_ROOT}/actors/{name}
    """

    @staticmethod
    def get(name):
        name = name.replace("_", " ")
        actor = graph.get_actor(name)
        if actor is not None:
            return actor.to_dict()
        else:
            abort(404, message="Actor {} doesn't exist".format(name))

    @staticmethod
    def put(name):
        name = name.replace("_", " ")
        actor = graph.get_actor(name)
        if actor is None:
            abort(404, message="Actor {} doesn't exist".format(name))
        else:
            changes = request.get_json()
            if changes is None:
                abort(400, message="Incorrect mimetype or invalid json")
            else:
                graph.add_actor(changes, external=True, actor=actor)
                return actor.to_dict()

    @staticmethod
    def delete(name):
        name = name.replace("_", " ")
        actor = graph.get_actor(name)
        if actor is None:
            abort(404, message="Actor {} doesn't exist".format(name))
        else:
            graph.delete_actor(actor)
