# Lead Generation Automation

A modular, open-source web scraping tool for lead generation, featuring advanced anti-blocking, deep crawling, data validation, and a Streamlit UI.

## Features
- Scrapes Google, Bing, Yahoo, DuckDuckGo for leads
- Extracts names, emails, phones, social links, company/website URLs
- Rotating user-agents, optional proxies, delays, stealth browsing
- Deep crawling: visits main, contact, about, team, and people pages for more contacts
- JavaScript rendering with Selenium (undetected-chromedriver)
- Captcha bypass (cloudscraper/2Captcha demo)
- Data validation (email, phone, URLs)
- Streamlit UI: keyword input, result count, progress, validation, CSV export
- **Headless mode toggle in UI** (choose visible or invisible browser)
- **Centralized config.py** for all project settings
- Robust error handling for configuration reloads
- Modular codebase: `scraper/`, `utils/`, `validators/`, `config.py`

## Setup
1. Clone this repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the UI:
   ```bash
   streamlit run app.py
   ```

## Usage
- Enter keywords, select result count, enable validation if needed
- Choose headless mode (no window) or visible browser in the UI
- Click Start to begin scraping
- Preview and download results as CSV

## Notes
- For best results, use headless mode for background runs, or visible mode for debugging/CAPTCHA
- All tools/libraries are free and open-source
- Deep crawling and JavaScript rendering are slow but maximize data
- All configuration is centralized in `config.py` and can be changed from the UI

---

**For development and troubleshooting, see comments in code and logs.** 