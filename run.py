from scrapy.crawler import CrawlerProcess
from model.crawler import Spider

if __name__ == "__main__":
    # disable logging
    # process = CrawlerProcess({"LOG_LEVEL": "CRITICAL"})
    process = CrawlerProcess()
    process.crawl(Spider)
    process.start()
