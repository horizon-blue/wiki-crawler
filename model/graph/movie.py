from sqlalchemy import Column, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Movie(Base):
    """
    The represent the movie nodes in the graph
    (SQLAlchemy model: movie)
    """

    def __init__(self):
        self.__tablename__ = 'movie'

        # data fields of movie
        self.name = Column(Text)
        self.wiki_page = Column(Text)

        # relationship to actors
        self.actors = relationship("Edge", back_populates="actor")
