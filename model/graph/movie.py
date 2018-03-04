from sqlalchemy import Column, Integer, Text, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, MINYEAR, MAXYEAR
from dateparser import parse as parse_date
from database import Base
from .util import get_wiki_page
from model.crawler import MovieItem


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

    def __init__(self, item=None):
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
        if not (isinstance(item, MovieItem) or isinstance(item, dict)):
            return
        self.name = item.get("name", self.name)
        self.box_office = item.get("box_office", 0 if self.box_office is None else self.box_office)
        self.wiki_page = get_wiki_page(item.get("wiki_page", self.wiki_page))

        self.release_date = item.get("release_date", self.release_date)

        # parse release date if it is string
        if isinstance(self.release_date, str):
            self.release_date = parse_date(self.release_date)

        # setup release date
        if self.release_date is None and "year" in item:
            year = item.get("year")
            if MINYEAR <= year <= MAXYEAR:
                self.release_date = datetime(year, 1, 1)

    def __repr__(self):
        """
        Representation of the node
        :return: a string representation of the node
        """
        return '<{} "{}">'.format(self.__class__.__name__, self.name)

    def to_dict(self):
        """
        A method to convert Movie class do dict
        :return: a dictionary represents a Movie
        """
        return {
            "id": self.id,
            "name": self.name,
            "wiki_page": self.wiki_page,
            "box_office": self.box_office,
            "release_date": self.release_date.strftime('%Y-%m-%d') if self.release_date else None,
            "actors": [edge.actor.name for edge in self.actors if edge.actor.name is not None],
        }
