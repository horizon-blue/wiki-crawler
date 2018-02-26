from scrapy.exceptions import DropItem
import os
import jsonpickle
from ..graph import Graph

JSON_OUTPUT_FILE = "output/out.json"


class GraphPipeline:
    graph = Graph()

    def close_spider(self, _):
        """
        Close the file object as the spider ends crawling
        :param _: reference to the spider object (unused)
        """
        # creates the directory if none exists
        # source: https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
        os.makedirs(os.path.dirname(JSON_OUTPUT_FILE), exist_ok=True)

        with open(JSON_OUTPUT_FILE, "w") as file:
            file.write(jsonpickle.encode(self.graph))

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
