from abc import ABC, abstractmethod


class Node(ABC):
    name = None

    @abstractmethod
    def __init__(self):
        ...

    def __str__(self):
        return self.name


class ActorNode(Node):
    age = None
    movies = {}

    def __init__(self, name, age):
        """
        Create a node to hold value for an actor
        :param name: name of the actor
        :param age: age of the actor
        """
        super(ActorNode, self).__init__()

        self.name = name
        self.age = age


class MovieNode(Node):
    income = None
    actors = {}

    def __init__(self, name, income, actors=None):
        """
        Create a node to hold value for a movie
        :param name: name of the movie
        :param income: gross income of the movie
        :param actors: list of actors, in the same order as they appears in wikipedia
        """
        super(MovieNode, self).__init__()

        self.name = name
        self.income = income
        if actors is not None:
            self.set_actors(actors)

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
            self.actors[actor] = 2 * (m + 1 - n) / (m * (m + 1))
