from unittest import TestCase
from model.graph import Graph
from model.crawler import MovieItem, ActorItem


class TestGraph(TestCase):
    def setUp(self):
        self.graph = Graph()
        self.actor_item = ActorItem(name="a", url="b", age=10)
        self.movie_item = MovieItem(name="x", url="y", income=12345, actors=["a", "b", "c"], release_date=None)

    def test_add_actor(self):
        self.graph.add(self.actor_item)
        self.assertEqual(self.graph.actors["b"].name, "a")

    def test_add_existed_actor(self):
        self.graph.add(self.movie_item)
        self.graph.add(self.actor_item)
        self.assertIn("y", self.graph.actors["b"].movies)

    def test_add_movie(self):
        self.graph.add(self.movie_item)
        self.assertEqual(self.graph.movies["y"].name, "x")
        self.assertEqual(len(self.graph.unreached_actors), 3)

    def test_add_existed_movie(self):
        movie_item2 = MovieItem(name="xyz", url="y", income=123, actors=["a"], release_date=None)
        self.graph.add(self.movie_item)
        movie_node = self.graph.movies["y"]
        self.graph.add(movie_item2)
        self.assertIs(movie_node, self.graph.movies["y"])

    def test_add_movie_with_existed_actor(self):
        self.graph.add(self.actor_item)
        self.graph.add(self.movie_item)
        self.assertIn("y", self.graph.actors["b"].movies)

    def test_dump_load(self):
        self.graph.add(self.movie_item)
        self.graph.add(self.actor_item)
        self.graph.dump("output/tmp.json")
        g = Graph.load("output/tmp.json")
        self.assertIn("b", self.graph.actors)
        self.assertIn("y", self.graph.movies)

    def test_get_movie(self):
        self.graph.add_movie(self.movie_item)
        movie_node = self.graph.movies["y"]
        # get movie by url
        self.assertEqual(movie_node, self.graph.get_movie("y"))
        # get movie by name
        self.assertEqual(movie_node, self.graph.get_movie("x"))
        # get non-exist movie
        self.assertIsNone(self.graph.get_movie("foo"))

    def test_get_actor(self):
        self.graph.add_actor(self.actor_item)
        actor_node = self.graph.actors["b"]
        # get actor by url
        self.assertEqual(actor_node, self.graph.get_actor("b"))
        # get actor by name
        self.assertEqual(actor_node, self.graph.get_actor("a"))
        # get non-exist actor
        self.assertIsNone(self.graph.get_actor("foo"))

    #
    # def test_get_gross_income(self):
    #     self.fail()
    #
    # def test_get_movies(self):
    #     self.fail()
    #
    # def test_get_actors(self):
    #     self.fail()
    #
    # def test_get_actor_rank(self):
    #     self.fail()
    #
    # def test_get_oldest_actors(self):
    #     self.fail()
    #
    # def test_get_movies_by_year(self):
    #     self.fail()
    #
    # def test_get_actors_by_year(self):
    #     self.fail()
    #
    # def test_get_counts(self):
    #     self.fail()
