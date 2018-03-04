from scrapy.exceptions import DropItem
from ..graph import Graph
from .item import MovieItem
from database import db_session
from config import JSON_OUTPUT_FILE, RESUME
import logging


class GraphPipeline:
    """
    The pipeline that process the items return by the crawler
    """
    graph = Graph(db_session)
    actor_count = 0
    movie_count = 0

    def open_spider(self, _):
        """
        Try to the graph (if any) when spider opens
        :param _: reference to the spider object (unused)
        """
        if RESUME and JSON_OUTPUT_FILE is not None:
            try:
                self.graph = Graph.load(JSON_OUTPUT_FILE)
                if not isinstance(self.graph, Graph):
                    self.graph = Graph()
            except FileNotFoundError:
                pass

    def close_spider(self, _):
        """
        Close the file object as the spider ends crawling
        :param _: reference to the spider object (unused)
        """
        if JSON_OUTPUT_FILE is not None:
            self.graph.dump(JSON_OUTPUT_FILE)

        db_session.remove()

    def process_item(self, item, _):
        """
        Add new item to the graph
        :param item: the item to add
        :param _: reference to the spider object (unused)
        :return: the item for used in later pipeline
        """
        try:
            if isinstance(item, MovieItem):
                if item.get("box_office") is None or not item.get("actors"):
                    raise ValueError("missing actors or income information")
            self.graph.add(item)
            if isinstance(item, MovieItem):
                self.movie_count += 1
            else:
                self.actor_count += 1

            # logging
            logging.info(
                "Processed {} at {}. "
                "Current Progress - movies: {}, actors: {}".format(
                    item.__class__.__name__, item["wiki_page"], self.movie_count, self.actor_count))
            return item
        except (KeyError, ValueError):
            raise DropItem("Incomplete info in %s" % item)
