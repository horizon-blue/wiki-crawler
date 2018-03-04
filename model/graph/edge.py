from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base


class Edge(Base):
    """
    The edge that connect movie ane actor and storing the amount of income that
    the actor obtained from the given movie
    """

    def __init__(self):
        self.__tablename__ = 'edge'
        # used to identify the edge
        self.movie_id = Column(Integer, ForeignKey('movie.id'), primary_key=True)
        self.actor_id = Column(Integer, ForeignKey('actor.id'), primary_key=True)

        # the data stored by the edge
        self.income = Column(Float)
        self.movie = relationship("Movie", back_populates="movies")
        self.actor = relationship("Actor", back_populates="actors")
