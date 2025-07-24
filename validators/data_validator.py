from config import HEADLESS_MODE

import re
from validate_email import validate_email
import phonenumbers
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
OBFUSCATED_EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+\s*\[at\]\s*[a-zA-Z0-9-]+\s*\[dot\]\s*[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d -]{8,}\d"
SOCIAL_REGEX = r"(linkedin|facebook|twitter|instagram)\\.com/[A-Za-z0-9_.-]+"
URL_REGEX = r"https?://[\w./-]+"

CRAWL_KEYWORDS = ["contact", "about", "team", "people", "staff", "directory"]


def extract_contacts(text):
    # Standard emails
    emails = re.findall(EMAIL_REGEX, text)
    valid_emails = [e for e in emails if validate_email(e)]
    # Obfuscated emails
    obf_emails = re.findall(OBFUSCATED_EMAIL_REGEX, text)
    for obf in obf_emails:
        decoded = (
            obf.replace("[at]", "@").replace("[dot]", ".")
            .replace(" at ", "@").replace(" dot ", ".")
            .replace(" AT ", "@").replace(" DOT ", ".")
            .replace("(at)", "@").replace("(dot)", ".")
            .replace("{at}", "@").replace("{dot}", ".")
            .replace(" ", "")
        )
        if validate_email(decoded):
            valid_emails.append(decoded)
    # Phones
    phones = re.findall(PHONE_REGEX, text)
    valid_phones = []
    for phone in phones:
        try:
            if phonenumbers.is_valid_number(phonenumbers.parse(phone, None)):
                valid_phones.append(phone)
        except:
            continue
    return valid_emails, valid_phones


def crawl_with_selenium(url, depth=2, visited=None):
    if visited is None:
        visited = set()
    emails, phones = [], []
    try:
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if HEADLESS_MODE:
            options.add_argument('--headless=new')
        driver = uc.Chrome(options=options)
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
        e, p = extract_contacts(html)
        emails.extend(e)
        phones.extend(p)
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            text = link.get_text().lower()
            if any(kw in href.lower() or kw in text for kw in CRAWL_KEYWORDS):
                if not href.startswith('http'):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                if href not in visited and depth > 1:
                    visited.add(href)
                    try:
                        driver.get(href)
                        time.sleep(2)
                        sub_html = driver.page_source
                        e2, p2 = extract_contacts(sub_html)
                        emails.extend(e2)
                        phones.extend(p2)
                    except:
                        continue
        driver.quit()
    except Exception as e:
        pass
    return list(set(emails)), list(set(phones))


def validate_lead(lead):
    snippet = lead.get('snippet', '')
    url = lead.get('url', '')
    # Extract from snippet
    snippet_emails, snippet_phones = extract_contacts(snippet)
    # Try to extract from linked page and crawl deeper
    page_emails, page_phones = [], []
    if url and url.startswith('http'):
        try:
            e, p = crawl_with_selenium(url, depth=2)
            page_emails.extend(e)
            page_phones.extend(p)
        except Exception as e:
            pass
    # Combine and deduplicate
    all_emails = list(set(snippet_emails + page_emails))
    all_phones = list(set(snippet_phones + page_phones))
    socials = re.findall(SOCIAL_REGEX, snippet)
    valid_url = bool(re.match(URL_REGEX, url))
    return {
        'name': lead.get('name', ''),
        'emails': ', '.join(all_emails),
        'phones': ', '.join(all_phones),
        'url': url,
        'valid_url': valid_url,
        'socials': socials,
        'snippet': snippet
    } 