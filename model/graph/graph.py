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
        actor_node = ActorNode(actor_item["name"], actor_item["age"])
        url = actor_item["url"]

        if url in self.actors:  # actor is already created by movie
            self.actors[url].update(actor_node)
        else:
            self.actors[url] = actor_node

    def add_movie(self, movie_item):
        """
        Create movie vertex for the given movie, and update all actors associate with
        the movie
        :param movie_item: the movie item to add
        """
        url = movie_item["url"]
        if url in self.movies:  # do nothing if move exists
            return
        movie_node = MovieNode(movie_item["name"], movie_item["income"], movie_item["actors"])
        self.movies[url] = movie_node

        for actor in movie_node.actors:
            if actor not in self.actors:  # create the actor for the movie
                self.actors[actor] = ActorNode()
            # link movie to actors
            self.actors[actor].add_movie(url, movie_node.get_actor_income(actor))

    @classmethod
    def load(cls, filename):
        """
        Load the graph from given file
        :param filename: the file to load the graph
        :return: the graph loaded
        """
        with open(filename) as file:
            return jsonpickle.decode(file.read())

    def dump(self, filename):
        """
        dump the graph to the specified file. this method creates the directory if
        none exists
        :param filename: the file to create
        """
        # creates the directory if none exists
        # source: https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as file:
            file.write(jsonpickle.encode(self))
