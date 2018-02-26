from .node import ActorNode, MovieNode
from ..crawler import ActorItem, MovieItem


class Graph:
    movies = {}
    actors = {}

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

        # link movie to actors
        for actor in movie_node.actors:
            self.actors[actor].add_movie(url, movie_node.get_actor_income(actor))
