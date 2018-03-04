import os
import jsonpickle
from .node import ActorNode, MovieNode
from ..crawler import ActorItem, MovieItem


class Graph:
    """
    The graph class that holds all nodes and edges
    """
    def __init__(self):
        """
        Initialize the graph with two kinds of nodes
        """
        self.movies = {}
        self.actors = {}

        # dictionary to store the url for given name
        self.urls = {}

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

    def add_url_map(self, name, url):
        """
        Helper function to associate name with url
        :param name: name of the node
        :param url: url of the node
        """
        self.urls[name] = url

    def add_actor(self, actor_item, url=""):
        """
        Create an actor vertex for the given vector, or merge to existing one
        :param actor_item: the ActorItem for the given actor
        :param url: a replacement url that overwrites the url in actor_item
        """
        url = actor_item.get("wiki_page", url) if url == "" else url

        if url in self.actors:  # actor is already created by movie
            self.actors[url].update(actor_item)
        else:
            self.actors[url] = ActorNode(actor_item)

        if "name" in actor_item and url != actor_item.get("name"):
            self.add_url_map(actor_item.get("name"), url)

    def add_movie(self, movie_item, url=""):
        """
        Create movie vertex for the given movie, and update all actors associate with
        the movie
        :param movie_item: the movie item to add
        :param url: a replacement url that overwrites the url in movie_item
        """
        url = movie_item.get("wiki_page", url) if url == "" else url
        if url in self.movies:  # do nothing if move exists
            return
        movie_node = MovieNode(movie_item)
        self.movies[url] = movie_node

        for actor in movie_node.actors:
            if actor not in self.actors:  # create the actor for the movie
                self.actors[actor] = ActorNode({"wiki_page": actor})
            # link movie to actors
            self.actors[actor].add_movie(url, movie_node.get_actor_income(actor))

        if "name" in movie_item and url != movie_item.get("name"):
            self.add_url_map(movie_item.get("name"), url)

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

    def get_movie(self, movie):
        """
        Query to get the movie node object based on its name or url
        :param movie: name or url of the movie
        :return: MovieNode, or None if no data is found
        """
        if movie in self.movies:
            return self.movies[movie]
        elif movie in self.urls:
            return self.movies[self.urls[movie]]
        else:
            return None

    def get_actor(self, actor):
        """
        Query to get the actor node object based on its name or url
        :param actor: name or url of the actor
        :return: ActorNode, or None if no data is found
        """
        if actor in self.actors:
            return self.actors[actor]
        elif actor in self.urls:
            return self.actors[self.urls[actor]]
        else:
            return None

    def get_box_office(self, movie):
        """
        Query to get the gross income given a movie url
        :param movie: the name or url of the movie
        :return: gross income of a movie, or None if no data is found
        """
        movie_node = self.get_movie(movie)
        if movie_node is not None:
            return movie_node.box_office

    def get_movies(self, actor):
        """
        Query to get the list of movies the given actor has worked in
        :param actor: the name or url of the actor
        :return: list of the movies that the actor is in, or None if no data is found
        """
        actor_node = self.get_actor(actor)
        if actor_node is not None:
            return [self.movies[movie] for movie in actor_node.movies]

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
