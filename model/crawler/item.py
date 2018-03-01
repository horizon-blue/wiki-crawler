from scrapy import Item as ScrapyItem, Field


class Item(ScrapyItem):
    """
    The based scrapy item for movie and actor
    """
    name = Field()
    wiki_page = Field()


class ActorItem(Item):
    """
    The scrapy item containing actor specific field
    """
    age = Field()


class MovieItem(Item):
    """
        The scrapy item containing movie specific fields
        """
    box_office = Field()
    actors = Field()
    release_date = Field()
