from scrapy import Spider as scrapySpider, Request
from bs4 import BeautifulSoup
from .Task import Task

DEFAULT_TASK = Task(url="https://en.wikipedia.org/wiki/Morgan_Freeman", is_movie=False)


class Spider(scrapySpider):
    name = "spider"
    allowed_domains = "en.wikipedia.org"
    start_tasks = []

    # using fake user-agent
    # source: https://github.com/alecxe/scrapy-fake-useragent
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
        },
    }

    def __init__(self, start_task=DEFAULT_TASK, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)

        self.start_tasks.append(start_task)

    def start_requests(self):
        """
        override default start_requests so that we can pass in is_movie information
        as metadata
        :return: iterable for each task
        """
        for task in self.start_tasks:
            yield Request(task.url, callback=self.parse, meta={'is_movie': task.is_movie})

    def parse(self, response):
        is_movie = response.meta["is_movie"]
        soup = BeautifulSoup(response.text, 'lxml')
        
        print(soup.find(id="firstHeading").text)
