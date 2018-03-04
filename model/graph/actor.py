from sqlalchemy import Column, Integer, Text, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from .node import Node
from model.crawler import ActorItem


class Actor(Base, Node):
    """
    The represent the actor nodes in the graph
    (SQLAlchemy model: actor)
    """

    __tablename__ = 'actor'
    id = Column(Integer, primary_key=True)

    # data fields of actor
    name = Column(Text)
    wiki_page = Column(Text, unique=True)
    age = Column(Integer)
    total_gross = Column(Float)

    # relationship to movies
    movies = relationship("Edge", back_populates="movie")

    def __init__(self, item=None):
        """
        Create a node to hold value for an actor
        :param item: the actor item or dict of the actor
        """
        super(Actor, self).__init__()

        self.update(item)

    def update(self, item):
        """
        Update current actor node using other actor node
        :param item: the item or dict representing other actor
        """
        if not (isinstance(item, ActorItem) or isinstance(item, dict)):
            return
        self.name = item.get("name", self.name)
        self.age = item.get("age", self.age)
        self.total_gross = item.get("total_gross", 0 if self.total_gross is None else self.total_gross)
        self.set_wiki_page(item.get("wiki_page", self.wiki_page))
