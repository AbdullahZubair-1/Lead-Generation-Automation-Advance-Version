import pandas as pd
from scraper.engine import ScraperEngine

scraper_instance = None

# Generator for progress and data

def start_scraping(keyword, num_results, validate):
    global scraper_instance
    scraper_instance = ScraperEngine(keyword, num_results, validate)
    for progress, data in scraper_instance.run():
        yield progress, data

def stop_scraping():
    global scraper_instance
    if scraper_instance:
        scraper_instance.stop() 