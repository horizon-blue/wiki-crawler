from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base


class Edge(Base):
    """
    The edge that connect movie ane actor and storing the amount of income that
    the actor obtained from the given movie
    """

    __tablename__ = 'edge'
    # used to identify the edge
    movie_id = Column(Integer, ForeignKey('movie.id'), primary_key=True)
    actor_id = Column(Integer, ForeignKey('actor.id'), primary_key=True)

    # the data stored by the edge
    income = Column(Float)
    movie = relationship("Movie", back_populates="actors")
    actor = relationship("Actor", back_populates="movies")

    def __repr__(self):
        """
        Representation of the node
        :return: a string representation of the node
        """
        return '<{} "{}" "{}">'.format(self.__class__.__name__, self.movie, self.actor)
