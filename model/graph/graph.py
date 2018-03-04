from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import extract
import os
import jsonpickle
from model.graph import Actor, Movie, Edge
from ..crawler import ActorItem, MovieItem


class Graph:
    """
    The graph class that holds all nodes and edges
    """

    def __init__(self, session=None):
        """
        Initialize the graph with two kinds of nodes
        :param session: the database session. If None is given,
        then the graph will creates its own session (remember to
        close the graph)
        """
        if session is None:
            from database import db_session
            self.session = db_session
            self.own_session = True
        else:
            if not isinstance(session, scoped_session):
                raise TypeError("'session' must be a scoped database session")
            self.session = session

    def __enter__(self):
        """
        Enable the use of "with"
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the session if the database session is owned by the graph itself
        """
        if self.own_session:
            self.session.remove()

    # noinspection PyTypeChecker
    def add(self, item):
        """
        Add the item to the graph based on its type
        :param item: the item to add
        """
        if isinstance(item, ActorItem):
            self.add_actor(item)
        elif isinstance(item, MovieItem):
            self.add_movie(item)

    def add_actor(self, actor_item, external=False):
        """
        Create an actor vertex for the given vector, or merge to existing one
        :param actor_item: the ActorItem for the given actor
        :param external: whether we are constructing from external data
        """
        # check if the given actor already existed, search by name or wiki page
        actor = self.get_actor(name=actor_item.get("name")).first() if external \
            else self.get_actor(wiki_page=actor_item.get("wiki_page")).first()

        if actor is None:
            actor = Actor(actor_item)
        else:
            actor.update(actor_item)
        self.session.add(actor)
        self.session.commit()

    def add_movie(self, movie_item, external=False):
        """
        Create movie vertex for the given movie, and update all actors associate with
        the movie
        :param movie_item: the movie item to add
        :param external: whether we are constructing from external data
        """
        movie = self.get_movie(name=movie_item.get("name")).first() if external \
            else self.get_movie(wiki_page=movie_item.get("wiki_page")).first()

        if movie is None:
            movie = Movie(movie_item)
        else:
            movie.update(movie_item)
        self.session.add(movie)

        # add relationship to actors
        # the nth actor have 2 * (m + 1 - n) / (m * (m + 1)) of the movies gross income
        actors = movie_item.get("actors")
        if isinstance(actors, list):
            m = len(actors)
            for index, actor_key in enumerate(actors):
                n = index + 1
                actor_filter = {"name": actor_key} if external else {"wiki_page": actor_key}
                actor = self.get_actor(**actor_filter).first()
                if actor is None:
                    actor = Actor(actor_filter)
                income = 2 * (m + 1 - n) / (m * (m + 1)) * movie_item.get("box_office", 0)
                # creates the relationship
                if movie.id is not None and actor.id is not None:
                    edge = Edge.query.filter_by(movie_id=movie.id, actor_id=actor.id).first()
                    if edge is not None:
                        edge.income = income
                        self.session.add(edge)
                        continue
                edge = Edge(actor=actor, movie=movie, income=income)
                self.session.add(edge)
        self.session.commit()

    @classmethod
    def load(cls, filename):
        """
        Load the graph from given file
        :param filename: the file to load the graph
        :return: the graph loaded
        """
        # with open(filename) as file:
        #     decoded = jsonpickle.decode(file.read())
        #     if isinstance(decoded, Graph):
        #         return decoded
        #     elif isinstance(decoded, list) and len(decoded) == 2:
        #         actors, movies = decoded
        #         graph = Graph()
        #         for movie_name, movie in movies.items():
        #             graph.add_movie(movie, movie_name)
        #         for actor_name, actor in actors.items():
        #             graph.add_actor(actor, actor_name)
        #         return graph

    def dump(self, filename):
        """
        dump the graph to the specified file. this method creates the directory if
        none exists
        :param filename: the file to create
        """
        # creates the directory if none exists
        # source: https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
        # dirname = os.path.dirname(filename)
        # if dirname != '':
        #     os.makedirs(dirname, exist_ok=True)
        #
        # with open(filename, "w") as file:
        #     file.write(jsonpickle.encode(self))

    @staticmethod
    def get_movie(**kwargs):
        """
        Query to get the movie node object based on its name or url
        :param kwargs: the filter used to select the movie
        :return: The movie query
        """
        return Movie.query.filter_by(**kwargs)

    @staticmethod
    def get_actor(**kwargs):
        """
        Query to get the actor node object based on its name or url
        :param kwargs: the filter used to select the actor
        :return: The actor query
        """
        return Actor.query.filter_by(**kwargs)

    def get_box_office(self, **kwargs):
        """
        Query to get the gross income given a movie url
        :param kwargs: query arguments to search the movie
        :return: gross income of a movie, or None if no data is found
        """
        movie = self.get_movie(**kwargs).first()
        if movie is not None:
            return movie.box_office

    def get_movies(self, **kwargs):
        """
        Query to get the list of movies the given actor has worked in
        :param kwargs: query arguments to search the actor
        :return: list of the movies that the first matching actor is in,
         or None if no data is found
        """
        actor = self.get_actor(**kwargs).first()
        if actor is not None:
            return

    def get_actors(self, **kwargs):
        """
        Query to get the list of actors the given movie has
        :param kwargs: query arguments to search the movie
        :return: list of the actors that the movie has, or None if no data is found
        """
        movie = self.get_movie(**kwargs).first()
        if movie is not None:
            return [edge.actor for edge in movie.actors]

    def get_actor_rank(self, n=10):
        """
        Get the top n actors with highest gross income
        :param n: the number of actors to get, or negative int to get all actors
        :return: a List containing n actor object. The returning list might be shorter
        than n if the total number of actors is smaller than n
        """
        return self.get_actor().order_by(Actor.total_gross.desc()).limit(n).all()

    def get_oldest_actors(self, n=10):
        """
        Get the oldest n actors
        :param n: the number of actors to get, or non-positive int to get all actors
        :return: a List containing n actor object. The returning list might be shorter
        than n if the total number of actors is smaller than n
        """
        return self.get_actor().order_by(Actor.age.desc()).limit(n).all()

    def get_movies_by_year(self, year):
        """
        Query to get all movies in a specified year
        :param year: the year to lookup
        :return: a list of MovieNode in a given year
        """
        return self.get_movie().filter(extract('year', Movie.release_date) == year).all()

    def get_actors_by_year(self, year):
        """
        Query to get all actors in a specified year
        :param year: the year to lookup
        :return: a list of ActorNode in a given year
        """
        # search through movie
        return self.get_actor().join(Edge).join(Movie).filter(extract('year', Movie.release_date) == year).all()
