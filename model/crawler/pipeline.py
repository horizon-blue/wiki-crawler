from scrapy.exceptions import DropItem


class GraphPipeline:
    def process_item(self, item, spider):
        print(type(item))
