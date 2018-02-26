import re
from scrapy import Spider as ScrapySpider, Request
from bs4 import BeautifulSoup
from dateparser import parse as parse_date
from .item import MovieItem, ActorItem
from . import config


ROOT = "https://en.wikipedia.org"


class Spider(ScrapySpider):
    """
    The main spider used to crawl wikipedia
    """
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
        "EXTENSIONS": {
            "scrapy.extensions.closespider.CloseSpider": 1,
        },
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": config.DELAY,
        "CLOSESPIDER_ITEMCOUNT": config.CLOSE_ITEM_COUNT,
        "CLOSESPIDER_TIMEOUT": config.CLOSE_TIMEOUT,
    }

    def __init__(self, start_task=(ROOT + config.START_URL, config.START_IS_MOVIE), *args, **kwargs):
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
        """
        Parse the response page based on type of page
        :param response: the response page
        :return: parsed Item or Request
        """
        if response.meta["is_movie"]:
            yield from self.parse_movie(response)
        else:
            yield from self.parse_actor(response)

    def parse_actor(self, response):
        """
        Parse the actor page from response
        :param response: the response page
        :return: parsed ActorItem or Request
        """
        try:
            soup = BeautifulSoup(response.text, 'lxml')

            name = re.sub(r"\(.*\)", "", soup.find(id="firstHeading").text).strip()

            info_box = soup.find("table", attrs={"class": "infobox"})
            age = self.get_age(info_box)
            # strip off root url
            link = response.request.url[len(ROOT):]

            movies = self.get_movies(soup)
            for movie_url in movies:
                yield Request(ROOT + movie_url, meta={'is_movie': True})

            # return the final parsed object
            yield ActorItem(name=name, age=age, url=link)
        except AttributeError:
            yield {}

    def parse_movie(self, response):
        """
        Parse the movie page from response
        :param response: the response page
        :return: parsed MovieItem or Request
        """
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            name = re.sub(r"\(.*\)", "", soup.find(id="firstHeading").text).strip()
            # strip off root url
            link = response.request.url[len(ROOT):]
            info_box = soup.find("table", attrs={"class": "infobox"})
            income = self.get_income(info_box)
            starring = self.get_starring(info_box)
            release_date = self.get_release_date(info_box)
            yield MovieItem(name=name, income=income, url=link, actors=starring, release_date=release_date)

            # generate new requests if there is income information
            if income is not None:
                for actor in starring:
                    yield Request(ROOT + actor, meta={'is_movie': False})
        except AttributeError:
            yield {}

    def get_movies(self, soup):
        """
        A helper method to get the url to movies from soup
        :param soup: the beautiful soup object
        :return: a list of movies
        """
        movies = []
        filmography = soup.find("span", id="Filmography").find_parent("h2").find_next_sibling()
        stop_token = "h2"

        while filmography.name != stop_token:  # stop at next h2
            # if contains film subsection, then read directly from there
            films = filmography.find(id="Film")
            if filmography.name == "h3" and films is not None:
                stop_token = "h3"
            urls = filmography.find_all("a")
            for url in urls:
                movies.append(url["href"])

            filmography = filmography.find_next_sibling()

        return movies

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
                age = info_box.find("span", attrs={"class": "dday deathdate"}) \
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
        except (AttributeError, TypeError):
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

    def get_release_date(self, info_box):
        """
        a helper method to get the release date of the movie
        :param info_box: the beautiful soup object of the info box
        :return: the release date of the movie, or None if cannot parse
        """
        try:
            release_date = info_box.find("span", attrs={"class": "published"}).text
            return parse_date(release_date)
        except AttributeError:
            return None