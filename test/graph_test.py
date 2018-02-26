from unittest import TestCase
from model.graph import Graph
from model.crawler import MovieItem, ActorItem


class TestGraph(TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_add_actor(self):
        actor_item = ActorItem(name="foo", url="bar", age=10)
        self.graph.add(actor_item)
        self.assertEqual(self.graph.actors["bar"].name, "foo")

    def test_add_movie(self):
        movie_item = MovieItem(name="foo", url="bar", income=12345, actors=["a", "b", "c"], release_date=None)
        self.graph.add(movie_item)
        self.assertEqual(self.graph.movies["bar"].name, "foo")
        self.assertEqual(len(self.graph.unreached_actors), 3)

    #
    # def test_load(self):
    #     self.fail()
    #
    # def test_dump(self):
    #     self.fail()
    #
    # def test_get_movie(self):
    #     self.fail()
    #
    # def test_get_actor(self):
    #     self.fail()
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
