from database import db_session, init_db, Base, engine
from unittest import TestCase
from model.crawler import ActorItem, MovieItem
from model.graph import Graph
from datetime import datetime

actor_item = ActorItem(name="a", wiki_page="b", age=10)
movie_item = MovieItem(name="x", wiki_page="y", box_office=12345,
                       actors=["a", "b", "c"], release_date=datetime(2018, 3, 4))


class TestAnalysis(TestCase):
    def setUp(self):
        init_db()
        self.graph = Graph(db_session)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        db_session.remove()

    def test_hub_actor(self):
        self.graph.add(actor_item)
        self.graph.add(movie_item)
        self.graph.add_actor({"name": "foo"})

        actors = self.graph.get_hub_actor()
        self.assertEqual(actors[0][0].name, "a")

        actors2 = self.graph.get_hub_actor(n=-1)
        self.assertEqual(len(actors), len(actors2))

        self.graph.get_hub_actor(plot=True, save_to="output/hub_actor.png")

    def test_age_correlation(self):
        self.graph.add(actor_item)
        self.graph.add(movie_item)
        self.graph.add_actor({"name": "foo", "wiki_page": "b", "age": 10})
        self.graph.add_actor({"name": "bar", "age": 20, "total_gross": 12345})

        actors = self.graph.get_age_correlation()
        self.assertEqual(actors[0][0], 20)

        self.graph.get_age_correlation(plot=True, save_to="output/age_correlation.png")
