from abc import ABC, abstractmethod
from datetime import datetime, MINYEAR, MAXYEAR

ROOT = "https://en.wikipedia.org"


class Node(ABC):
    """
    The abstract Node class for vertices in graph
    """
    name = None
    wiki_page = None

    def set_wiki_page(self, url):
        """
        A helper function to set the wiki page
        :param url: the link to wiki page
        """
        if isinstance(url, str) and url.startswith(ROOT):
            url = url[len(ROOT):]
        self.wiki_page = url

    @abstractmethod
    def __init__(self):
        ...

    def __repr__(self):
        """
        Representation of the node
        :return: a string representation of the node
        """
        return '<{} "{}">'.format(self.__class__.__name__, self.name)


class ActorNode(Node):
    """
    The subclass of Node used to store actor information
    """

    def __init__(self, actor_item=None):
        """
        Create a node to hold value for an actor
        :param actor_item: the actor item or dict of the actor
        """
        super(ActorNode, self).__init__()

        if actor_item is None:
            actor_item = {}

        self.name = actor_item.get("name")
        self.age = actor_item.get("age")
        self.total_gross = actor_item.get("total_gross", 0)
        self.set_wiki_page(actor_item.get("wiki_page"))

        self.movies = dict((movie, 0) for movie in actor_item.get("movies", []))

    def update(self, other):
        """
        Update current actor node using other actor node
        :param other: the other actor node
        """
        if not isinstance(other, ActorNode):
            return
        self.age = other.age
        self.name = other.name
        self.movies.update(other.movies)
        # re-calculate the income
        self.total_gross = 0
        for movie in self.movies:
            self.total_gross += self.movies[movie]

    def add_movie(self, movie, income):
        """
        Associate actor with the movie and update the actors total income
        :param movie: link to the movie
        :param income: income that the actor get from the movie
        """
        # overwrite existed value
        if movie in self.movies:
            self.total_gross -= self.movies[movie]

        self.movies[movie] = income
        self.total_gross += income


class MovieNode(Node):
    """
    The subclass used to store movie information
    """

    def __init__(self, movie_item):
        """
        Create a node to hold value for a movie
        :param movie_item: the MovieItem object or dict of the movie
        """
        super(MovieNode, self).__init__()

        self.name = movie_item.get("name")
        self.box_office = movie_item.get("box_office", 0)
        self.set_wiki_page(movie_item.get("wiki_page"))

        self.release_date = movie_item.get("release_date")

        # setup release date
        if self.release_date is None and "year" in movie_item:
            year = movie_item.get("year")
            if MINYEAR <= year <= MAXYEAR:
                self.release_date = datetime(year, 1, 1)

        self.actors = {}
        self.set_actors(movie_item.get("actors", []))

    def set_actors(self, actors):
        """
        set the list of actors (url) for the movie and calculate the income for each of
        the actor. Assume that the n-th actor in the list have
        2 * (m + 1 - n) / (m * (m + 1)) of the movies gross income, where m = len(actors)
        :param actors: list of actors, in the same order as they appears in wikipedia
        :return: None
        """
        m = len(actors)
        for index, actor in enumerate(actors):
            n = index + 1
            self.actors[actor] = self.box_office * 2 * (m + 1 - n) / (m * (m + 1))

    def get_actor_income(self, actor):
        """
        Helper function to get the income a specific actor received from a movie
        :param actor: the actor to look up
        :return: income an actor received from a movie
        """
        if actor in self.actors:
            return self.actors[actor]
        else:
            return 0
