from scrapy.crawler import CrawlerProcess
from model.crawler import Spider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(Spider)
    process.start()
