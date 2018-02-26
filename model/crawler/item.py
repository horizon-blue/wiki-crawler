from scrapy import Item as ScrapyItem, Field


class Item(ScrapyItem):
    name = Field()
    url = Field()


class ActorItem(Item):
    age = Field()


class MovieItem(Item):
    income = Field()
    actors = Field()
