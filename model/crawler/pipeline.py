from scrapy.exceptions import DropItem
from ..graph import Graph
from config import JSON_OUTPUT_FILE
import logging


class GraphPipeline:
    """
    The pipeline that process the items return by the crawler
    """
    graph = Graph()

    def open_spider(self, _):
        """
        Try to the graph (if any) when spider opens
        :param _: reference to the spider object (unused)
        """
        if JSON_OUTPUT_FILE is not None:
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

    def process_item(self, item, _):
        """
        Add new item to the graph
        :param item: the item to add
        :param _: reference to the spider object (unused)
        :return: the item for used in later pipeline
        """
        try:
            self.graph.add(item)
            count = self.graph.get_counts()
            # logging
            logging.info(
                "Processed {} at {}. "
                "Current Progress - movies: {}, actors: {}".format(
                    item.__class__.__name__, item["url"], count[0], count[1]))
            return item
        except (KeyError, ValueError):
            raise DropItem("Incomplete info in %s" % item)
