from config import HEADLESS_MODE

import undetected_chromedriver as uc
import time
import random
from utils.proxy_manager import get_proxy
from utils.ua_manager import get_user_agent
from loguru import logger
from bs4 import BeautifulSoup

class DuckDuckGoSpider:
    def __init__(self, keyword, num_results, stop_event):
        self.keyword = keyword
        self.num_results = num_results
        self.stop_event = stop_event

    def scrape(self, q):
        logger.info(f'DuckDuckGoSpider: Starting browser for keyword: {self.keyword}')
        ua = get_user_agent()
        proxy = get_proxy()
        options = uc.ChromeOptions()
        options.add_argument(f'user-agent={ua}')
        if HEADLESS_MODE:
            options.add_argument('--headless=new')
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            logger.info(f'DuckDuckGoSpider: Using proxy {proxy}')
        else:
            logger.info('DuckDuckGoSpider: No proxy used')
        try:
            driver = uc.Chrome(options=options)
            logger.info('DuckDuckGoSpider: Browser started')
            driver.get(f'https://duckduckgo.com/?q={self.keyword}&t=h_&ia=web')
            logger.info('DuckDuckGoSpider: Page loaded')
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1, 2))
            html = driver.page_source
            # Save HTML for debugging
            with open('duckduckgo_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info('DuckDuckGoSpider: Saved HTML to duckduckgo_debug.html')
            driver.quit()
            logger.info('DuckDuckGoSpider: Page source retrieved and browser closed')
            soup = BeautifulSoup(html, 'lxml')
            # Try robust selectors for DuckDuckGo
            selectors = [
                ('div.result', soup.select('div.result')),
                ('article[data-nrn="result"]', soup.select('article[data-nrn="result"]')),
                ('div[data-testid="result"]', soup.select('div[data-testid="result"]')),
            ]
            for sel, matches in selectors:
                logger.info(f'DuckDuckGoSpider: Selector {sel} found {len(matches)} containers')
            results = next((matches for _, matches in selectors if matches), [])
            logger.info(f'DuckDuckGoSpider: Using {len(results)} result containers')
            count = 0
            for r in results:
                if (self.stop_event is not None and self.stop_event.is_set()) or count >= self.num_results:
                    break
                try:
                    a = r.find('a', href=True)
                    url = a['href'] if a else ''
                    title_tag = r.find('h2') or r.find('span', {'class': 'result__title'})
                    name = title_tag.get_text(strip=True) if title_tag else ''
                    snippet_tag = r.find('a', {'class': 'result__snippet'}) or r.find('div', {'class': 'result__snippet'})
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else r.get_text(strip=True)
                    logger.info(f'DuckDuckGoSpider: Found lead: {name}, {url}')
                    q.put({'name': name, 'url': url, 'snippet': snippet})
                    count += 1
                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.error(f'DuckDuckGoSpider error (result parse): {e}')
            logger.info(f'DuckDuckGoSpider: Finished scraping {count} leads')
        except Exception as e:
            logger.error(f'DuckDuckGoSpider error (main): {e}')
        q.put('DONE') 