from scrapy.exceptions import DropItem
from ..graph import Graph
from config import JSON_OUTPUT_FILE


class GraphPipeline:
    """
    The pipeline that process the items return by the crawler
    """
    graph = Graph()

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
            return item
        except (KeyError, ValueError):
            raise DropItem("Incomplete info in %s" % item)
