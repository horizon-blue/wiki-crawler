from scrapy.exceptions import DropItem
from ..graph import Graph


class GraphPipeline:
    graph = Graph()

    def process_item(self, item, spider):
        """
        Add new item to the graph
        :param item: the item to add
        :param spider: reference to the spider object
        """
        try:
            self.graph.add(item)
        except KeyError:
            raise DropItem("Incomplete info in %s" % item)
