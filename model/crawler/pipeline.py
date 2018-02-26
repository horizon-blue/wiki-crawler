from scrapy.exceptions import DropItem
from ..graph import Graph


class GraphPipeline:
    graph = Graph()

    def process_item(self, item, spider):
        """
        Add new item to the graph
        :param item: the item to add
        :param spider: reference to the spider object
        :return: the item for used in later pipeline
        """
        try:
            self.graph.add(item)
            return item
        except (KeyError, ValueError):
            raise DropItem("Incomplete info in %s" % item)
