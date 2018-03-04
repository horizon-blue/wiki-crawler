from sqlalchemy.orm.scoping import scoped_session
import os
import jsonpickle
from model.graph import Actor, Movie, Edge
from ..crawler import ActorItem, MovieItem
from .util import get_filter


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

    def commit(self):
        """
        A helper function to commit the changes made in current session
        """
        self.session.commit()

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

    def add_actor(self, actor_item):
        """
        Create an actor vertex for the given vector, or merge to existing one
        :param actor_item: the ActorItem for the given actor
        """
        # check if the given actor already existed, search by name or wiki page
        actor_filter = get_filter(actor_item)
        actor = self.get_actor(**actor_filter).first() if actor_filter else None

        if actor is None:
            actor = Actor(actor_item)
        else:
            actor.update(actor_item)
        self.session.add(actor)

    def add_movie(self, movie_item, external=False):
        """
        Create movie vertex for the given movie, and update all actors associate with
        the movie
        :param movie_item: the movie item to add
        :param external: whether we are constructing from external data
        """
        movie_filter = get_filter(movie_item)
        movie = self.get_actor(**movie_filter).first() if movie_filter else None

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
                actor = self.get_actor(name=actor_key).first() if external \
                    else self.get_actor(wiki_page=actor_key).first()
                if actor is None:
                    actor = Actor({})

    @classmethod
    def load(cls, filename):
        """
        Load the graph from given file
        :param filename: the file to load the graph
        :return: the graph loaded
        """
        with open(filename) as file:
            decoded = jsonpickle.decode(file.read())
            if isinstance(decoded, Graph):
                return decoded
            elif isinstance(decoded, list) and len(decoded) == 2:
                actors, movies = decoded
                graph = Graph()
                for movie_name, movie in movies.items():
                    graph.add_movie(movie, movie_name)
                for actor_name, actor in actors.items():
                    graph.add_actor(actor, actor_name)
                return graph

    def dump(self, filename):
        """
        dump the graph to the specified file. this method creates the directory if
        none exists
        :param filename: the file to create
        """
        # creates the directory if none exists
        # source: https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
        dirname = os.path.dirname(filename)
        if dirname != '':
            os.makedirs(dirname, exist_ok=True)

        with open(filename, "w") as file:
            file.write(jsonpickle.encode(self))

    def get_movie(self, **kwargs):
        """
        Query to get the movie node object based on its name or url
        :param kwargs: the filter used to select the movie
        :return: The movie query
        """
        return Movie.query.filter_by(**kwargs)

    def get_actor(self, **kwargs):
        """
        Query to get the actor node object based on its name or url
        :param kwargs: the filter used to select the actor
        :return: The actor query
        """
        return Actor.query.filter_by(**kwargs)

    def get_box_office(self, movie):
        """
        Query to get the gross income given a movie url
        :param movie: the name or url of the movie
        :return: gross income of a movie, or None if no data is found
        """
        movie_node = self.get_movie(movie)
        if movie_node is not None:
            return movie_node.box_office

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

    def get_actors(self, movie):
        """
        Query to get the list of actors the given movie has
        :param movie: the name or url of the movie
        :return: list of the actors that the movie has, or None if no data is found
        """
        movie_node = self.get_movie(movie)
        if movie_node is not None:
            return [self.actors[actor] for actor in movie_node.actors if actor in self.actors]

    def get_actor_rank(self, n=10):
        """
        Get the top n actors with highest gross income
        :param n: the number of actors to get, or non-positive int to get all actors
        :return: a List containing n actor object. The returning list might be shorter
        than n if the total number of actors is smaller than n
        """
        actor_rank = sorted((actor for actor in self.actors.values() if actor.total_gross is not None),
                            key=lambda actor: actor.total_gross, reverse=True)
        if n > 0:
            return actor_rank[:n]
        return actor_rank

    def get_oldest_actors(self, n=10):
        """
        Get the oldest n actors
        :param n: the number of actors to get, or non-positive int to get all actors
        :return: a List containing n actor object. The returning list might be shorter
        than n if the total number of actors is smaller than n
        """
        actor_rank = sorted((actor for actor in self.actors.values() if actor.age is not None),
                            key=lambda actor: actor.age, reverse=True)
        if n > 0:
            return actor_rank[:n]
        return actor_rank

    def get_movies_by_year(self, year):
        """
        Query to get all movies in a specified year
        :param year: the year to lookup
        :return: a list of MovieNode in a given year
        """
        return [movie for movie in self.movies.values()
                if movie.release_date is not None and movie.release_date.year == year]

    def get_actors_by_year(self, year):
        """
        Query to get all actors in a specified year
        :param year: the year to lookup
        :return: a list of ActorNode in a given year
        """
        movies = self.get_movies_by_year(year)
        actors = set()
        for movie in movies:
            actors.update((self.actors[actor] for actor in movie.actors if actor in self.actors))
        return list(actors)

    def get_counts(self):
        """
        Get the number of movies and actors crawled
        :return: (movie_count, actor_count) tuple
        """
        return len(self.movies), len(self.actors)
