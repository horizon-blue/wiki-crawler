from unittest import TestCase
from model.graph import Graph
from model.crawler import MovieItem, ActorItem
from datetime import datetime


class TestGraph(TestCase):
    def setUp(self):
        self.graph = Graph()
        self.actor_item = ActorItem(name="a", url="b", age=10)
        self.movie_item = MovieItem(name="x", url="y", income=12345, actors=["a", "b", "c"],
                                    release_date=datetime(2018, 3, 4))

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

    def test_get_gross_income(self):
        self.graph.add(self.movie_item)
        self.assertEqual(self.movie_item["income"], self.graph.get_gross_income("x"))
        # check gross income for each actor equals to the income of movie
        total_income = 0
        for actor_income in self.graph.movies["y"].actors.values():
            total_income += actor_income
        self.assertAlmostEqual(total_income, self.graph.get_gross_income("y"))

    def test_get_movies(self):
        self.graph.add(self.movie_item)
        self.graph.add(self.actor_item)
        movie_node = self.graph.get_movie("y")
        movie_nodes = self.graph.get_movies("b")
        self.assertIn(movie_node, movie_nodes)
        self.assertEqual(len(movie_nodes), 1)

    def test_get_actors(self):
        self.graph.add(self.movie_item)
        self.graph.add(self.actor_item)
        actor_item2 = ActorItem(name="foo", url="a", age=10)
        self.graph.add(actor_item2)
        actor_node = self.graph.get_actor("b")
        actor_nodes = self.graph.get_actors("y")
        self.assertIn(actor_node, actor_nodes)
        self.assertEqual(len(actor_nodes), 2)

    def test_get_actor_rank(self):
        self.graph.add(self.movie_item)
        self.graph.add(self.actor_item)
        actor_item2 = ActorItem(name="foo", url="a", age=10)
        self.graph.add(actor_item2)
        actor_rank = self.graph.get_actor_rank(2)
        actor_rank2 = self.graph.get_actor_rank(-1)
        self.assertIs(self.graph.get_actor("foo"), actor_rank[0])
        self.assertIs(self.graph.get_actor("b"), actor_rank[1])
        self.assertEqual(actor_rank, actor_rank2)

    def test_get_oldest_actors(self):
        self.graph.add(self.movie_item)
        self.graph.add(self.actor_item)
        actor_item2 = ActorItem(name="foo", url="a", age=12)
        self.graph.add(actor_item2)
        actor_rank = self.graph.get_oldest_actors(2)
        actor_rank2 = self.graph.get_oldest_actors(-1)
        self.assertIs(self.graph.get_actor("foo"), actor_rank[0])
        self.assertIs(self.graph.get_actor("b"), actor_rank[1])
        self.assertEqual(actor_rank, actor_rank2)

    def setup_movie_years(self):
        movie_item2 = MovieItem(name="xyz", url="z", income=12345, actors=["a", "b", "c"],
                                release_date=datetime(2018, 1, 1))
        movie_item3 = MovieItem(name="opq", url="q", income=12345, actors=["a", "b", "c"],
                                release_date=datetime(2008, 2, 3))
        self.graph.add(self.movie_item)
        self.graph.add(movie_item2)
        self.graph.add(movie_item3)

    def test_get_movies_by_year(self):
        self.setup_movie_years()
        movies = self.graph.get_movies_by_year(2018)
        self.assertEqual(len(movies), 2)
        self.assertNotIn(self.graph.get_movie("q"), movies)

    def test_get_actors_by_year(self):
        self.setup_movie_years()
        self.graph.add(self.actor_item)
        actor_item2 = ActorItem(name="foo", url="a", age=12)
        self.graph.add(actor_item2)
        actors = self.graph.get_actors_by_year(2018)
        self.assertEqual(len(actors), 2)

    def test_get_counts(self):
        self.setup_movie_years()
        self.graph.add(self.actor_item)
        actor_item2 = ActorItem(name="foo", url="a", age=12)
        self.graph.add(actor_item2)

        movie_count, actor_count = self.graph.get_counts()
        self.assertEqual(movie_count, 3)
        self.assertEqual(actor_count, 2)
