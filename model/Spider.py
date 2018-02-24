import scrapy

DEFAULT_URL = "https://en.wikipedia.org/wiki/Morgan_Freeman"


class Spider(scrapy.Spider):
    name = "spider"
    allowed_domains = "en.wikipedia.org"
    start_urls = []

    # using fake user-agent
    # source: https://github.com/alecxe/scrapy-fake-useragent
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
        }
    }

    def __init__(self, start_url=DEFAULT_URL, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)

        self.start_urls.append(start_url)

    def parse(self, response):
        print(response)
