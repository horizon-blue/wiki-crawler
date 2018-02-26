from scrapy.crawler import CrawlerProcess
from model.crawler import Spider

if __name__ == "__main__":
    # disable logging
    process = CrawlerProcess()
    process.crawl(Spider)
    process.start()
