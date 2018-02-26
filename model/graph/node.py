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
    income = 0
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
        self.income = 0
        for movie in self.movies:
            self.income += self.movies[movie]

    def add_movie(self, movie, income):
        """
        Associate actor with the movie and update the actors total income
        :param movie: link to the movie
        :param income: income that the actor get from the movie
        """
        # overwrite existed value
        if movie in self.movies:
            self.income -= self.movies[movie]

        self.movies[movie] = movie
        self.income += income


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
        if income is None:
            raise ValueError("Income cannot be None")
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
            self.actors[actor] = self.income * 2 * (m + 1 - n) / (m * (m + 1))

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
