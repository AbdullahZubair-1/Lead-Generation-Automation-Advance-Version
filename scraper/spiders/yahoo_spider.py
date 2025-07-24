from config import HEADLESS_MODE

import undetected_chromedriver as uc
import time
import random
from utils.proxy_manager import get_proxy
from utils.ua_manager import get_user_agent
from loguru import logger
from bs4 import BeautifulSoup

class YahooSpider:
    def __init__(self, keyword, num_results, stop_event):
        self.keyword = keyword
        self.num_results = num_results
        self.stop_event = stop_event

    def scrape(self, q):
        logger.info(f'YahooSpider: Starting browser for keyword: {self.keyword}')
        ua = get_user_agent()
        proxy = get_proxy()
        options = uc.ChromeOptions()
        options.add_argument(f'user-agent={ua}')
        if HEADLESS_MODE:
            options.add_argument('--headless=new')
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            logger.info(f'YahooSpider: Using proxy {proxy}')
        else:
            logger.info('YahooSpider: No proxy used')
        try:
            driver = uc.Chrome(options=options)
            logger.info('YahooSpider: Browser started')
            driver.get(f'https://search.yahoo.com/search?p={self.keyword}')
            logger.info('YahooSpider: Page loaded')
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1, 2))
            html = driver.page_source
            driver.quit()
            logger.info('YahooSpider: Page source retrieved and browser closed')
            soup = BeautifulSoup(html, 'lxml')
            results = soup.select('div.dd.algo')
            logger.info(f'YahooSpider: Found {len(results)} result containers')
            count = 0
            for r in results:
                if (self.stop_event is not None and self.stop_event.is_set()) or count >= self.num_results:
                    break
                try:
                    name = r.select_one('h3').text if r.select_one('h3') else ''
                    url = r.select_one('a')['href'] if r.select_one('a') else ''
                    snippet = r.text
                    logger.info(f'YahooSpider: Found lead: {name}, {url}')
                    q.put({'name': name, 'url': url, 'snippet': snippet})
                    count += 1
                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.error(f'YahooSpider error (result parse): {e}')
            logger.info(f'YahooSpider: Finished scraping {count} leads')
        except Exception as e:
            logger.error(f'YahooSpider error (main): {e}')
        q.put('DONE') 