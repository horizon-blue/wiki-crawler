from scrapy import Spider as ScrapySpider, Request
from bs4 import BeautifulSoup

ROOT = "https://en.wikipedia.org"
DEFAULT_START_URL = ROOT + "/wiki/Michael_Jackson"
DEFAULT_IS_MOVIE = False


class Spider(ScrapySpider):
    name = "spider"
    allowed_domains = ["en.wikipedia.org"]
    start_tasks = []

    # using fake user-agent
    # source: https://github.com/alecxe/scrapy-fake-useragent
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
        },
        "DOWNLOAD_DELAY": 0.25,
    }

    def __init__(self, start_task=(DEFAULT_START_URL, DEFAULT_IS_MOVIE), *args, **kwargs):
        """
        Initialize a movie crawler
        :param start_task: the first page to start crawling. this should be a (url, is_movie)
        pair, where url is a string indicating the first page to crawl and is_movie indicates
        whether the first page is movie page or not
        :param args: other arguments to pass into the super class
        :param kwargs: other arguments to pass into the super class
        """
        super(Spider, self).__init__(*args, **kwargs)

        self.start_tasks.append(start_task)

    def start_requests(self):
        """
        override default start_requests so that we can pass in is_movie information
        as metadata
        :return: iterable for each task
        """
        for task in self.start_tasks:
            url, is_movie = task
            yield Request(url, meta={'is_movie': is_movie})

    def parse(self, response):
        if response.meta["is_movie"]:
            yield from self.parse_movie(response)
        else:
            yield from self.parse_actor(response)

    def parse_actor(self, response):

        soup = BeautifulSoup(response.text, 'lxml')

        name = soup.find(id="firstHeading").text
        age = self.get_age(soup)
        movies = []

        # get all links before next h2 tag
        filmography = soup.find("span", id="Filmography").find_parent("h2").find_next_sibling()

        while filmography.name != "h2":
            urls = filmography.find_all("a")
            for url in urls:
                href = url["href"]
                movies.append(href)
                # scrapy filters duplicated urls on default
                yield Request(ROOT + href, meta={'is_movie': True})
                break
            filmography = filmography.find_next_sibling()

    def get_age(self, soup):
        """
        A helper class to get the age of current actor
        :param soup: the beautiful soup object for the entire page
        :return: age of the actor, or none if cannot find anything
        """
        # try to find the current age of actor, if he/she is still alive
        try:
            age = soup.find("span", attrs={"class": "noprint ForceAgeToShow"})
            if age is not None:
                # the actor is still alive
                age = age.text
            else:
                # the actor is dead.. need to find the death information
                age = soup.find("span", attrs={"class": "dday deathdate"}) \
                    .find_parent().find_next_sibling().previous_element

            # gather all digits in age description (age xxx) or (aged xxx)
            return int("".join(c for c in age if c.isdigit()))

        except AttributeError:
            # cannot parse the age
            return None

    def parse_movie(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        yield {}
