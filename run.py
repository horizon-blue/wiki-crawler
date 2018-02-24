from scrapy.crawler import CrawlerProcess
from model import Spider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(Spider)
    process.start()
