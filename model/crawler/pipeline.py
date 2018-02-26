from scrapy.exceptions import DropItem
from ..graph import Graph

JSON_OUTPUT_FILE = "output/out.json"


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
            print("Movies: %d, Actors: %d" % self.graph.get_counts())
            return item
        except (KeyError, ValueError):
            raise DropItem("Incomplete info in %s" % item)
