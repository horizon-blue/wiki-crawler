from scrapy import Spider as ScrapySpider, Request
import re
from bs4 import BeautifulSoup
from .item import MovieItem, ActorItem

ROOT = "https://en.wikipedia.org"
DEFAULT_START_URL = ROOT + "/wiki/Morgan_Freeman"
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
        "ITEM_PIPELINES": {
            "model.crawler.pipeline.GraphPipeline": 300,
        },
        "DOWNLOAD_DELAY": 1,
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
        try:
            soup = BeautifulSoup(response.text, 'lxml')

            name = soup.find(id="firstHeading").text

            info_box = soup.find("table", attrs={"class": "infobox"})
            age = self.get_age(info_box)
            # strip off root url
            link = response.request.url[len(ROOT):]

            # get all links before next h2 tag
            filmography = soup.find("span", id="Filmography").find_parent("h2").find_next_sibling()

            while filmography.name != "h2":
                urls = filmography.find_all("a")
                for url in urls:
                    href = url["href"]
                    # scrapy filters duplicated urls on default
                    yield Request(ROOT + href, meta={'is_movie': True})
                filmography = filmography.find_next_sibling()
            # return the final parsed object
            yield ActorItem(name=name, age=age, url=link)
        except AttributeError:
            yield {}

    def parse_movie(self, response):
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            name = soup.find(id="firstHeading").text
            # strip off root url
            link = response.request.url[len(ROOT):]
            info_box = soup.find("table", attrs={"class": "infobox"})
            income = self.get_income(info_box)
            starring = self.get_starring(info_box)
            yield MovieItem(name=name, income=income, url=link, actors=starring)

            # generate new requests
            for actor in starring:
                yield Request(ROOT + actor, meta={'is_movie': False})
        except AttributeError:
            yield {}

    def get_age(self, info_box):
        """
        A helper method to get the age of current actor
        :param info_box: info_box: the beautiful soup object for the info box
        :return: age of the actor, or none if cannot find anything
        """
        # try to find the current age of actor, if he/she is still alive
        try:
            age = info_box.find("span", attrs={"class": "noprint ForceAgeToShow"})
            if age is not None:
                # the actor is still alive
                age = age.text
            else:
                # the actor is dead.. need to find the death information
                age = soup.find("span", attrs={"class": "dday deathdate"}) \
                    .find_parent().find_next_sibling().previous_element
            # gather all digits in age description (age xxx) or (aged xxx)
            return int(re.search(r"aged?\D*(\d+)", age).group(1))

        except AttributeError:
            # cannot parse the age
            return None

    def get_income(self, info_box):
        """
        A helper method to get the box office of current film
        :param info_box: the beautiful soup object for the info box
        :return: gross income of the film, or none if cannot find anything
        """
        try:
            income = info_box.find(text="Box office").find_parent() \
                .find_next_sibling().next_element
            return self.parse_currency(income)
        except AttributeError:
            return None

    def get_starring(self, info_box):
        """
        A helper method to get all actors for a given movie
        :param info_box: the beautiful soup object for the info box
        :return: a list of links to actors (in the same order as they are listed in wikipedia)
        """
        try:
            starring = info_box.find(text="Starring").find_parent("tr")
            return [url["href"] for url in starring.find_all("a")]
        except AttributeError:
            return []

    def parse_currency(self, income):
        """
        A helper method to convert string representation of income to float that
        represent the value
        :param income: the string representation of income
        :return: the income as float, or None if income cannot be parsed
        """
        try:
            # use regular expression to remove everything in parenthesis, if any
            income = re.sub(r"\(.*\)", "", income).strip()

            # remove currency symbol, million/billion endings and comma
            income_value = float(income.strip("$mbtrillion").replace(',', ''))

            # augmented by the endings
            if income.endswith("million"):
                income_value *= 1e6
            elif income.endswith("billion"):
                income_value *= 1e9
            elif income.endswith("trillion"):
                income_value *= 1e12
            return income_value

        except ValueError:
            return None
