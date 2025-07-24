from config import HEADLESS_MODE

import undetected_chromedriver as uc
from fake_useragent import UserAgent
import time
import random
from utils.proxy_manager import get_proxy
from utils.ua_manager import get_user_agent
from utils.captcha_solver import bypass_captcha
from loguru import logger
from bs4 import BeautifulSoup
import cloudscraper

class GoogleSpider:
    def __init__(self, keyword, num_results, stop_event):
        self.keyword = keyword
        self.num_results = num_results
        self.stop_event = stop_event

    def scrape(self, q):
        logger.info(f'GoogleSpider: Starting browser for keyword: {self.keyword}')
        ua = get_user_agent()
        proxy = get_proxy()
        options = uc.ChromeOptions()
        options.add_argument(f'user-agent={ua}')
        if HEADLESS_MODE:
            options.add_argument('--headless=new')
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            logger.info(f'GoogleSpider: Using proxy {proxy}')
        else:
            logger.info('GoogleSpider: No proxy used')
        try:
            driver = uc.Chrome(options=options)
            logger.info('GoogleSpider: Browser started')
            driver.get(f'https://www.google.com/search?q={self.keyword}')
            logger.info('GoogleSpider: Page loaded')
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1, 2))
            html = driver.page_source
            # Save HTML for debugging
            with open('google_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info('GoogleSpider: Saved HTML to google_debug.html')
            driver.quit()
            logger.info('GoogleSpider: Page source retrieved and browser closed')
            soup = BeautifulSoup(html, 'lxml')
            # Try multiple selectors for robustness
            selectors = [
                ('div[data-sokoban-container="true"]', soup.select('div[data-sokoban-container="true"]')),
                ('div.g', soup.select('div.g')),
                ('div.MjjYud', soup.select('div.MjjYud')),
                ('div.tF2Cxc', soup.select('div.tF2Cxc')),
            ]
            for sel, matches in selectors:
                logger.info(f'GoogleSpider: Selector {sel} found {len(matches)} containers')
            # Use the first non-empty selector
            results = next((matches for _, matches in selectors if matches), [])
            logger.info(f'GoogleSpider: Using {len(results)} result containers')
            count = 0
            for r in results:
                if self.stop_event is not None and self.stop_event.is_set() or count >= self.num_results:
                    break
                try:
                    # Try to extract title, url, and snippet robustly
                    h3 = r.find('h3')
                    name = h3.get_text(strip=True) if h3 else ''
                    a = r.find('a', href=True)
                    url = a['href'] if a else ''
                    snippet_tag = r.find('span', {'class': 'aCOpRe'}) or r.find('div', {'class': 'VwiC3b'})
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else r.get_text(strip=True)
                    logger.info(f'GoogleSpider: Found lead: {name}, {url}')
                    q.put({'name': name, 'url': url, 'snippet': snippet})
                    count += 1
                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.error(f'GoogleSpider error (result parse): {e}')
            logger.info(f'GoogleSpider: Finished scraping {count} leads')
        except Exception as e:
            logger.error(f'GoogleSpider error (main): {e}')
        q.put('DONE') 