from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy import extract, func, and_
from operator import itemgetter
import matplotlib.pyplot as plt
import json
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

    def add_actor(self, actor_item, external=False, actor=None):
        """
        Create an actor vertex for the given vector, or merge to existing one
        :param actor_item: the ActorItem for the given actor
        :param external: whether we are constructing from external data
        :param actor: the actor object to receive updates
        """
        if actor is None:
            # check if the given actor already existed, search by name or wiki page
            actor = self.get_actors(name=actor_item.get("name")).first() if external \
                else self.get_actors(wiki_page=actor_item.get("wiki_page")).first()

        if actor is None:
            actor = Actor(actor_item)
        else:
            actor.update(actor_item)
        self.session.add(actor)

        try:
            self.session.commit()
        except (IntegrityError, InvalidRequestError):  # unlikely to happen, but just in case
            self.session.rollback()

        movies = actor_item.get("movies")
        if isinstance(movies, list):
            for movie_key in movies:
                movie_filter = {"movie_name": movie_key} if external else {"movie_wiki_page": movie_key}
                self.add_edge(None, actor, **movie_filter)

    def add_movie(self, movie_item, external=False, movie=None):
        """
        Create movie vertex for the given movie, and update all actors associate with
        the movie
        :param movie_item: the movie item to add
        :param external: whether we are constructing from external data
        :param movie: the movie object to receive updates
        """
        if movie is None:
            movie = self.get_movies(name=movie_item.get("name")).first() if external \
                else self.get_movies(wiki_page=movie_item.get("wiki_page")).first()

        if movie is None:
            movie = Movie(movie_item)
        else:
            movie.update(movie_item)
        self.session.add(movie)

        try:
            self.session.commit()
        except (IntegrityError, InvalidRequestError):  # unlikely to happen, but just in case
            self.session.rollback()

        # add relationship to actors
        # the nth actor have 2 * (m + 1 - n) / (m * (m + 1)) of the movies gross income
        actors = movie_item.get("actors")
        if isinstance(actors, list):
            m = len(actors)
            for index, actor_key in enumerate(actors):
                n = index + 1
                actor_filter = {"actor_name": actor_key} if external else {"actor_wiki_page": actor_key}
                # do not calculate edge weight if importing external data
                income = 2 * (m + 1 - n) / (m * (m + 1)) * movie_item.get("box_office", 0) if not external else 0
                self.add_edge(income, movie=movie, **actor_filter)

    def add_edge(self, value, actor=None, movie=None, **kwargs):
        """
        A helper function to safely add edge without danger of creating duplicate edge. If
        actor and movie are specified, the actor_name and movie_name arguments are ignored
        :param value: the value stored on the edge
        :param actor: Actor object
        :param movie: Movie object
        :param kwargs: the rest filter used to select actor and movie if no object if found
        :return: the Edge object
        """
        if actor is None:
            actor_dict = {key[len("actor_"):]: val for key, val in kwargs.items() if key.startswith("actor_")}
            actor = self.get_actors(**actor_dict).first()
            # non exists
            if actor is None:
                actor = Actor(actor_dict)
        if movie is None:
            movie_dict = {key[len("movie_"):]: val for key, val in kwargs.items() if key.startswith("movie_")}
            movie = self.get_movies(**movie_dict).first()
            # non exists
            if movie is None:
                movie = Movie(movie_dict)

        # find edge

        edge = Edge.query.filter_by(movie=movie, actor=actor).first() if movie.id and actor.id else None
        if edge is None:
            edge = Edge(actor=actor, movie=movie, income=value)
        elif value is not None:
            actor.total_gross -= edge.income
            edge.income = value

        if value:
            actor.total_gross += value

        self.session.add(movie)
        self.session.add(actor)
        self.session.add(edge)

        try:
            self.session.commit()
        except (IntegrityError, InvalidRequestError):  # unlikely to happen, but just in case
            self.session.rollback()

        return edge

    @classmethod
    def load(cls, filename, session=None):
        """
        Load the graph from given file
        :param filename: the file to load the graph
        :return: the graph loaded
        """
        with open(filename) as file:
            decoded = json.load(file)
            if isinstance(decoded, list) and len(decoded) == 2:
                actors, movies = decoded
                graph = Graph(session)
                movies = movies.values() if isinstance(movies, dict) else movies
                actors = actors.values() if isinstance(actors, dict) else actors
                for movie in movies:
                    graph.add_movie(movie, external=True)
                for actor in actors:
                    graph.add_actor(actor, external=True)
                return graph

    @staticmethod
    def get_movies(**kwargs):
        """
        Query to get the movie node object based on its name or url
        :param kwargs: the filter used to select the movie
        :return: The movie query
        """
        return Movie.query.filter_by(**kwargs)

    @staticmethod
    def get_actors(**kwargs):
        """
        Query to get the actor node object based on its name or url
        :param kwargs: the filter used to select the actor
        :return: The actor query
        """
        return Actor.query.filter_by(**kwargs)

    @staticmethod
    def get_actor(name):
        """
        A helper function to get actor by name
        :param name: name of the actor, case insensitive
        :return: the first actor with matching name
        """
        return Actor.query.filter(func.lower(Actor.name) == func.lower(name)).first()

    @staticmethod
    def get_movie(name):
        """
        A helper function to get movie by name
        :param name: name of the movie, case insensitive
        :return: the first movie with matching name
        """
        return Movie.query.filter(func.lower(Movie.name) == func.lower(name)).first()

    def delete_actor(self, actor):
        """
        helper method to delete the given Actor object
        :param actor:
        :return:
        """
        self.session.delete(actor)
        self.session.commit()

    def delete_movie(self, movie):
        self.session.delete(movie)
        self.session.commit()

    def get_box_office(self, **kwargs):
        """
        Query to get the gross income given a movie url
        :param kwargs: query arguments to search the movie
        :return: gross income of a movie, or None if no data is found
        """
        movie = self.get_movies(**kwargs).first()
        if movie is not None:
            return movie.box_office

    def get_movies_for_actor(self, **kwargs):
        """
        Query to get the list of movies the given actor has worked in
        :param kwargs: query arguments to search the actor
        :return: list of the movies that the first matching actor is in,
         or None if no data is found
        """
        actor = self.get_actors(**kwargs).first()
        if actor is not None:
            return

    def get_actors_for_movie(self, **kwargs):
        """
        Query to get the list of actors the given movie has
        :param kwargs: query arguments to search the movie
        :return: list of the actors that the movie has, or None if no data is found
        """
        movie = self.get_movies(**kwargs).first()
        if movie is not None:
            return [edge.actor for edge in movie.actors]

    def get_actor_rank(self, n=10):
        """
        Get the top n actors with highest gross income
        :param n: the number of actors to get, or negative int to get all actors
        :return: a List containing n actor object. The returning list might be shorter
        than n if the total number of actors is smaller than n
        """
        return self.get_actors().order_by(Actor.total_gross.desc()).limit(n).all()

    def get_oldest_actors(self, n=10):
        """
        Get the oldest n actors
        :param n: the number of actors to get, or non-positive int to get all actors
        :return: a List containing n actor object. The returning list might be shorter
        than n if the total number of actors is smaller than n
        """
        return self.get_actors().order_by(Actor.age.desc()).limit(n).all()

    def get_movies_by_year(self, year):
        """
        Query to get all movies in a specified year
        :param year: the year to lookup
        :return: a list of MovieNode in a given year
        """
        return self.get_movies().filter(extract('year', Movie.release_date) == year).all()

    def get_actors_by_year(self, year):
        """
        Query to get all actors in a specified year
        :param year: the year to lookup
        :return: a list of ActorNode in a given year
        """
        # search through movie
        return self.get_actors().join(Edge).join(Movie).filter(extract('year', Movie.release_date) == year).all()

    # data analysis methods
    def get_hub_actor(self, plot=False, n=10, save_to=None):
        """
        Get the hub actor in the graph. If plot=True, then a bar graph for the
        top n actor is plotted
        :param plot: boolean, indicates whether or not to plot the chart
        :param n: the number of actors to plot
        :param save_to: the file name to save the plot
        :return: a list of (actor, count) tuple, sorted in decreasing order
        """
        connection_count = []
        actors = self.get_actors().all()
        for actor in actors:
            if not actor.movies:
                connection_count.append((actor, 0))
                continue
            # storing unique actor id
            neighbour_ids = set()
            for edge in actor.movies:
                neighbour_ids.update(other_edge.actor_id for other_edge in edge.movie.actors)
            # remove self
            neighbour_ids.remove(actor.id)
            connection_count.append((actor, len(neighbour_ids)))

        # sort actor by neighbour count
        connection_count.sort(key=itemgetter(1), reverse=True)

        n = min(n, len(connection_count))
        if n <= 0:
            n = len(connection_count)
        connection_count = connection_count[:n]

        if plot:
            plt.cla()
            plt.clf()

            actors, count = zip(*connection_count)
            plt.barh(range(n), count)
            plt.yticks(range(n), (actor.name for actor in actors))
            for idx, value in enumerate(count):
                plt.text(value + 3, idx, str(value))
            plt.title("Top {} Hub Actors".format(n))
            if save_to:
                plt.savefig(save_to)
            else:
                plt.show()

        return connection_count

    @staticmethod
    def get_age_correlation(plot=False, save_to=None):
        """
        Get the age group vs total income graph. If plot=True, then a bar graph for the
        top n actor is plotted
        :param plot: boolean, indicates whether or not to plot the chart
        :param save_to: the file name to save the plot
        :return: a list of (age_group, total_income) tuple, sorted in decreasing order
        """
        income_dict = {}
        # noinspection PyComparisonWithNone
        actors = Actor.query.filter(and_(Actor.age != None, Actor.total_gross != None)).all()

        for actor in actors:
            income_dict[actor.age] = income_dict.get(actor.age, 0) + actor.total_gross

        income_list = sorted(income_dict.items(), key=itemgetter(1), reverse=True)

        if plot:
            plt.cla()
            plt.clf()

            plt.scatter([actor.age for actor in actors],
                        [actor.total_gross for actor in actors])
            plt.xlabel("Age of Actors")
            plt.ylabel("Total Gross of Actors")
            plt.yscale("symlog")  # use symlog instead of log to preserve zero value
            plt.title("Correlation between actors and incomes")
            if save_to:
                plt.savefig(save_to)
            else:
                plt.show()
        return income_list
