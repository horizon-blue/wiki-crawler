from sqlalchemy import Column, Integer, Text, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, MINYEAR, MAXYEAR

from database import Base
from .node import Node


class Movie(Base, Node):
    """
    The represent the movie nodes in the graph
    (SQLAlchemy model: movie)
    """

    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)

    # data fields of movie
    name = Column(Text)
    wiki_page = Column(Text, unique=True)
    box_office = Column(Float)
    release_date = Column(DateTime)

    # relationship to actors
    actors = relationship("Edge", back_populates="actor")

    def __init__(self, movie_item):
        """
        Create a node to hold value for a movie
        :param movie_item: the MovieItem object or dict of the movie
        """
        super(Movie, self).__init__()

        self.name = movie_item.get("name")
        self.box_office = movie_item.get("box_office", 0)
        self.set_wiki_page(movie_item.get("wiki_page"))

        self.release_date = movie_item.get("release_date")

        # setup release date
        if self.release_date is None and "year" in movie_item:
            year = movie_item.get("year")
            if MINYEAR <= year <= MAXYEAR:
                self.release_date = datetime(year, 1, 1)
