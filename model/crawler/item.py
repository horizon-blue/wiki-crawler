from scrapy import Item as ScrapyItem, Field


class Item(ScrapyItem):
    """
    The based scrapy item for movie and actor
    """
    name = Field()
    url = Field()


class ActorItem(Item):
    """
    The scrapy item containing actor specific field
    """
    age = Field()


class MovieItem(Item):
    """
        The scrapy item containing movie specific fields
        """
    income = Field()
    actors = Field()
    release_date = Field()
