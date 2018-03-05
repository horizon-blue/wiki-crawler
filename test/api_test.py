from unittest import TestCase
from database import db_session, init_db, Base, engine
import json
from model.graph import Graph, Actor, Edge
from server import app


class TestAPI(TestCase):
    def setUp(self):
        init_db()
        self.app = app.test_client()
        self.graph = Graph.load('output/data_small.json', db_session)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_actors(self):
        response = self.app.get("/api/actors")
        actors = json.loads(response.data)

        self.assertIsNotNone(actors)
        self.assertEqual(len(actors), 23)

    def test_movies(self):
        response = self.app.get("/api/movies")
        movies = json.loads(response.data)
        self.assertIsNotNone(movies)
        self.assertEqual(len(movies), 44)

    def test_specific_actor(self):
        response = self.app.get("/api/actors/bruce_willis")
        actor = json.loads(response.data)

        self.assertIsNotNone(actor)
        self.assertEqual(actor.get("name"), "Bruce Willis")
        self.assertEqual(actor.get("age"), 61)
        self.assertAlmostEqual(actor.get("total_gross"), 562709189)
        self.assertEqual(len(actor.get("movies")), 19)

    def test_not_existed_actor(self):
        self.assertEqual(self.app.get("/api/actors/asdf").status_code, 404)
        self.assertEqual(self.app.put("/api/actors/asdf").status_code, 404)
        self.assertEqual(self.app.delete("/api/actors/asdf").status_code, 404)

    def test_not_existed_movie(self):
        self.assertEqual(self.app.get("/api/movies/asdf").status_code, 404)
        self.assertEqual(self.app.put("/api/movies/asdf").status_code, 404)
        self.assertEqual(self.app.delete("/api/movies/asdf").status_code, 404)

    def test_specific_movie(self):
        response = self.app.get("/api/movies/Die_Hard")
        movie = json.loads(response.data)

        self.assertIsNotNone(movie)
        self.assertEqual(movie.get("name"), "Die Hard")
        self.assertEqual(movie.get("release_date"), "1988-01-01")
        self.assertEqual(movie.get("wiki_page"), "/wiki/Die_Hard")
        self.assertAlmostEqual(movie.get("box_office"), 140)
        self.assertEqual(len(movie.get("actors")), 4)

    def test_invalid_query(self):
        response = self.app.get("/api/actors?asdf")
        self.assertEqual(response.status_code, 400)
        response = self.app.get("/api/movies?asdf")
        self.assertEqual(response.status_code, 400)

    def test_put_actor(self):
        response = self.app.put("/api/actors/Faye_Dunaway", data='{"age": 23}')
        self.assertEqual(response.status_code, 400)

        response = self.app.put("/api/actors/Faye_Dunaway", data='{"age": 23}', content_type='application/json')
        actor = json.loads(response.data)

        self.assertIsNotNone(actor)
        self.assertEqual(actor.get("name"), "Faye Dunaway")
        self.assertEqual(actor.get("age"), 23)

    def test_put_movie(self):
        response = self.app.put("/api/movies/Sunset", data='{"box_office": 2345}')
        self.assertEqual(response.status_code, 400)

        response = self.app.put("/api/movies/Sunset", data='{"box_office": 2345}', content_type='application/json')
        movie = json.loads(response.data)

        self.assertIsNotNone(movie)
        self.assertEqual(movie.get("name"), "Sunset")
        self.assertEqual(movie.get("box_office"), 2345)

    def test_post_actor(self):
        response = self.app.post("/api/actors", data=json.dumps({"name": "foo", "age": 3}))
        self.assertEqual(response.status_code, 400)

        response = self.app.post("/api/actors", data=json.dumps({"name": "foo", "age": 3}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        actor = json.loads(response.data)
        self.assertEqual(actor.get("name"), "foo")
        self.assertEqual(actor.get("age"), 3)

    def test_post_movie(self):
        response = self.app.post("/api/movies", data=json.dumps({"name": "foo", "box_office": 233}))
        self.assertEqual(response.status_code, 400)

        response = self.app.post("/api/movies", data=json.dumps({"name": "foo", "box_office": 233}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        movie = json.loads(response.data)
        self.assertEqual(movie.get("name"), "foo")
        self.assertEqual(movie.get("box_office"), 233)

    def test_delete(self):
        actor_url = "/api/actors/Faye_Dunaway"
        self.assertEqual(self.app.get(actor_url).status_code, 200)
        self.app.delete(actor_url)
        self.assertEqual(self.app.get(actor_url).status_code, 404)
        movie_url = "/api/movies/Sunset"
        self.assertEqual(self.app.get(movie_url).status_code, 200)
        self.app.delete(movie_url)
        self.assertEqual(self.app.get(movie_url).status_code, 404)

    def get_actor_query(self, query):
        actor_url = "/api/actors?"
        return json.loads(self.app.get(actor_url + query).data)

    def get_movie_query(self, query):
        movie_url = "api/movies?"
        return json.loads(self.app.get(movie_url + query).data)

    def test_actor_query(self):
        actors = self.get_actor_query("name=Willis")
        self.assertEqual(len(actors), 1)

    def test_movie_query(self):
        movies = self.get_movie_query("name=Hard")
        self.assertEqual(len(movies), 1)
