from unittest import TestCase
from model.graph import ActorNode, MovieNode
from datetime import datetime


class TestGraph(TestCase):
    def setUp(self):
        self.actor_node = ActorNode("foo", 23)
        self.movie_node = MovieNode("bar", 1234, datetime(2018, 1, 1), actors=["a"])

    def test_get_actor_income(self):
        self.assertAlmostEqual(1234, self.movie_node.get_actor_income("a"))
        self.assertEqual(0, self.movie_node.get_actor_income("b"))

    def test_add_movie_for_actor(self):
        self.actor_node.add_movie("a", 123)
        self.assertAlmostEqual(self.actor_node.income, 123)
        # replace previous movie
        self.actor_node.add_movie("a", 234)
        self.assertAlmostEqual(self.actor_node.income, 234)

    @classmethod
    def setup_raise_except(cls):
        MovieNode("foo", None, None, None)

    def test_raise_except(self):
        self.assertRaises(ValueError, TestGraph.setup_raise_except)

    def test_update_other_type(self):
        self.actor_node.update(self.movie_node)
        self.assertEqual("foo", self.actor_node.name)
