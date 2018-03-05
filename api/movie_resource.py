from flask_restful import Resource, abort
from flask import request
from sqlalchemy import and_, or_, extract
from database import db_session
from model.graph import Actor, Edge, Movie, Graph
from .util import parse_query

BOX_OFFICE_RANGE = 5000
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
            query_filter.append(Movie.name.contains(query.get("name")))
        if "year" in query:
            try:
                year = int(query.get("year"))
                query_filter.append(extract('year', Movie.release_date) == year)
            except ValueError:
                ...  # skip this argument
        if "wiki_page" in query:
            query_filter.append(Movie.wiki_page.contains(query.get("name")))
        if "box_office" in query:
            try:
                gross = float(query.get("total_gross"))
                query_filter.append(and_(Movie.box_office >= gross - BOX_OFFICE_RANGE,
                                         Movie.box_office <= gross + BOX_OFFICE_RANGE))
            except ValueError:
                ...  # skip this argument
        if "actor" in query or "actors" in query:
            actor_list = [query.get("actor")] if "actor" in query else query.get("actors").split(',')
            query_filter.append(and_(*[Movie.actors.any(Edge.actor.has(Actor.name.contains(actor_name.strip())))
                                       for actor_name in actor_list]))
        filters.append(and_(*query_filter))
    return or_(*filters)


class MovieQueryResource(Resource):
    """
    The Flask-Restful Resource class used for creating
    API for Movie query
    """

    def get(self):
        queries = parse_query(request.query_string.decode("utf-8"))
        return [movie.to_dict() for movie in Movie.query.filter(generate_query(queries)).all()]


class MovieResource(Resource):
    """
    The Flask-Restful Resource class used for creating
    API for a single Movie
    """

    def get(self, name):
        name = name.replace("_", " ")
        movie = graph.get_movie(name)
        if movie is not None:
            return movie.to_dict()
        else:
            abort(404, message="Movie {} doesn't exist".format(name))
