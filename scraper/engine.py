import pandas as pd
import queue
from scraper.spiders.google_spider import GoogleSpider
from scraper.spiders.bing_spider import BingSpider
from scraper.spiders.yahoo_spider import YahooSpider
from scraper.spiders.duckduckgo_spider import DuckDuckGoSpider
from utils.proxy_manager import get_proxy
from utils.ua_manager import get_user_agent
from validators.data_validator import validate_lead
from loguru import logger

class ScraperEngine:
    def __init__(self, keyword, num_results, validate):
        self.keyword = keyword
        self.num_results = num_results
        self.validate = validate
        self.data = []
        self.progress = 0
        self.total = num_results * 4  # 4 engines

    def run(self):
        spiders = [
            GoogleSpider(self.keyword, self.num_results, None),
            BingSpider(self.keyword, self.num_results, None),
            YahooSpider(self.keyword, self.num_results, None),
            DuckDuckGoSpider(self.keyword, self.num_results, None)
        ]
        q = queue.Queue()
        for spider in spiders:
            spider.scrape(q)
        finished = 0
        while not q.empty():
            item = q.get()
            if item == 'DONE':
                finished += 1
            else:
                if self.validate:
                    item = validate_lead(item)
                self.data.append(item)
                self.progress += 1
                yield int(100 * self.progress / self.total), pd.DataFrame(self.data)
        yield 100, pd.DataFrame(self.data)

    def stop(self):
        pass  # No threading, so nothing to stop 