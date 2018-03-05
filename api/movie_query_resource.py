from flask_restful import Resource
from flask import request
from sqlalchemy import and_, or_, extract
from model.graph import Actor, Edge, Movie
from .util import parse_query

BOX_OFFICE_RANGE = 5000


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
    API for Actor
    """

    def get(self):
        queries = parse_query(request.query_string.decode("utf-8"))
        return [movie.to_dict() for movie in Movie.query.filter(generate_query(queries)).all()]
