from sqlalchemy import Column, Integer, Text, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, MINYEAR, MAXYEAR
from database import Base
from .util import get_wiki_page


class Movie(Base):
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
    actors = relationship("Edge", back_populates="movie")

    def __init__(self, item):
        """
        Create a node to hold value for a movie
        :param movie_item: the MovieItem object or dict of the movie
        """
        super(Movie, self).__init__()

        self.update(item)

    def update(self, item):
        """
        Update current movie node using other actor node
        :param item: the item or dict representing other movie
        """
        self.name = item.get("name", self.name)
        self.box_office = item.get("box_office", 0 if self.box_office is None else self.box_office)
        self.wiki_page = get_wiki_page(item.get("wiki_page", self.wiki_page))

        self.release_date = item.get("release_date", self.release_date)

        # setup release date
        if self.release_date is None and "year" in item:
            year = item.get("year")
            if MINYEAR <= year <= MAXYEAR:
                self.release_date = datetime(year, 1, 1)
