import re
from scrapy import Spider as ScrapySpider, Request
from bs4 import BeautifulSoup
from dateparser import parse as parse_date
from .item import MovieItem, ActorItem
import config

ROOT = "https://en.wikipedia.org"


class Spider(ScrapySpider):
    """
    The main spider used to crawl wikipedia
    """
    name = "spider"
    allowed_domains = ["en.wikipedia.org"]
    start_tasks = [(ROOT + config.START_URL, config.START_IS_MOVIE, config.START_IS_FILMOGRAPHY)]

    custom_settings = {
        # using fake user-agent
        # source: https://github.com/alecxe/scrapy-fake-useragent
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
        },
        "ITEM_PIPELINES": {
            "model.crawler.pipeline.GraphPipeline": 300,
        },
        # use with CLOSESPIDER_ITEMCOUNT and CLOSESPIDER_TIMEOUT to set a condition
        # to shut down the spider
        "EXTENSIONS": {
            "scrapy.extensions.closespider.CloseSpider": 1,
        },
        "CLOSESPIDER_ITEMCOUNT": config.CLOSE_ITEM_COUNT,
        "CLOSESPIDER_TIMEOUT": config.CLOSE_TIMEOUT,
        # avoid robot detection
        "COOKIES_ENABLED": False,
        # delay between two consecutive request
        "DOWNLOAD_DELAY": config.DELAY,
        # directory to store paused spider
        "JOBDIR": config.JOBDIR,
    }

    def start_requests(self):
        """
        override default start_requests so that we can pass in is_movie information
        as metadata
        :return: iterable for each task
        """
        for task in self.start_tasks:
            url, is_movie, is_filmography = task
            yield Request(url, meta={'is_movie': is_movie, 'is_filmography': is_filmography})

    def parse(self, response):
        """
        Parse the response page based on type of page
        :param response: the response page
        :return: parsed Item or Request
        """
        if response.meta["is_movie"]:
            yield from self.parse_movie(response)
        elif response.meta["is_filmography"]:
            yield from self.parse_filmography(response)
        else:
            yield from self.parse_actor(response)

    def parse_actor(self, response):
        """
        Parse the actor page from response
        :param response: the response page
        :return: parsed ActorItem or Request
        """
        try:
            soup, name, link, info_box = self.parse_basic_info(response)
            age = self.get_age(info_box)

            movies, filmography_list = self.get_movies(soup)
            for movie_url in movies:
                yield Request(ROOT + movie_url, meta={'is_movie': True, 'is_filmography': False})
            for filmography in filmography_list:
                yield Request(ROOT + filmography, meta={'is_movie': False, 'is_filmography': True})

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
            soup, name, link, info_box = self.parse_basic_info(response)
            income = self.get_income(info_box)
            starring = self.get_starring(info_box)
            release_date = self.get_release_date(info_box)
            yield MovieItem(name=name, income=income, url=link, actors=starring, release_date=release_date)

            # generate new requests if there is income information
            if income is not None:
                for actor in starring:
                    yield Request(ROOT + actor, meta={'is_movie': False, 'is_filmography': False})
        except AttributeError:
            yield {}

    def parse_basic_info(self, response):
        """
        A helper function to parse the basic information on a page
        :param response:
        """
        soup = BeautifulSoup(response.text, 'lxml')
        name = re.sub(r"\(.*\)", "", soup.find(id="firstHeading").text).strip()
        # only store the last part (the xxx in https://en.wikipedia.org/wiki/xxx)
        link = response.request.url.rsplit('/')[-1]
        info_box = soup.find("table", attrs={"class": "infobox"})
        return soup, name, link, info_box

    def parse_filmography(self, response):
        """
        Parse the filmography page from response
        :param response: the response page
        :return: parsed Requests
        """
        urls = BeautifulSoup(response.text, 'lxml').find_all("a")
        for url in urls:
            if url.has_attr('href'):
                # fetch each movies
                yield Request(ROOT + url["href"], meta={'is_movie': True})

    def get_movies(self, soup):
        """
        A helper method to get the url to movies from soup
        :param soup: the beautiful soup object
        :return: a list of movies
        """
        movies = []
        filmography_list = []
        filmography = soup.find("span", id="Filmography").find_parent("h2").find_next_sibling()
        stop_token = "h2"

        while filmography.name != stop_token:  # stop at next h2
            # if contains film subsection, then read directly from there
            films = filmography.find(id="Film")
            if filmography.name == "h3" and films is not None:
                stop_token = "h3"
            urls = filmography.find_all("a")
            for url in urls:
                href = url["href"]
                # goes to filmography page instead
                if href.endswith("filmography"):
                    filmography_list.append(href)
                else:
                    movies.append(href)

            filmography = filmography.find_next_sibling()

        return movies, filmography_list

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
            return [url["href"] for url in starring.find_all("a").rsplit('/')[-1]]
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
