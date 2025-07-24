import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import streamlit as st
import pandas as pd
import time
from utils.data_handler import clean_and_export_data
from scraper.controller import start_scraping, stop_scraping
from validators.data_validator import validate_lead
import config

st.set_page_config(page_title="Lead Generation Automation", layout="wide")

if 'scraping' not in st.session_state:
    st.session_state['scraping'] = False
if 'progress' not in st.session_state:
    st.session_state['progress'] = 0
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame()
if 'validated_data' not in st.session_state:
    st.session_state['validated_data'] = pd.DataFrame()

st.title("Lead Generation Automation")

with st.form("scrape_form"):
    keyword = st.text_input("Enter keyword(s) for search:")
    num_results = st.selectbox("Number of results:", [10, 20, 50, 100, 1000])
    validate = st.checkbox("Enable data validation (after scraping)", value=True)
    headless = st.checkbox("Run browser in headless mode (no window)", value=config.HEADLESS_MODE)
    submitted = st.form_submit_button("Start Scraping")

table_placeholder = st.empty()
progress_placeholder = st.empty()

if submitted and not st.session_state['scraping']:
    # Update config.py with the user's headless choice
    with open('config.py', 'w') as f:
        f.write(f"HEADLESS_MODE = {headless}  # Set to False to see the browser, True to run headless\n")
    import importlib
    import sys
    if "config" in sys.modules:
        importlib.reload(sys.modules["config"])
    else:
        import config

    st.session_state['scraping'] = True
    st.session_state['progress'] = 0
    st.session_state['data'] = pd.DataFrame()
    st.session_state['validated_data'] = pd.DataFrame()

    for progress, data in start_scraping(keyword, num_results, False):
        st.session_state['progress'] = progress
        st.session_state['data'] = data
        progress_placeholder.progress(progress)
        table_placeholder.dataframe(data)
        time.sleep(0.1)

    st.session_state['scraping'] = False

if st.session_state['scraping']:
    progress_placeholder.progress(st.session_state['progress'])
    table_placeholder.dataframe(st.session_state['data'])
else:
    if not st.session_state['data'].empty:
        st.success("Scraping complete!")
        # Optionally validate after scraping
        if validate and st.session_state['validated_data'].empty:
            with st.spinner("Validating data..."):
                validated = [validate_lead(row) for row in st.session_state['data'].to_dict(orient='records')]
                st.session_state['validated_data'] = pd.DataFrame(validated)
        if validate and not st.session_state['validated_data'].empty:
            st.dataframe(st.session_state['validated_data'].head(20))
            st.download_button("Download Validated CSV", clean_and_export_data(st.session_state['validated_data']), file_name="leads_validated.csv", mime="text/csv")
            st.write(f"Total results: {len(st.session_state['validated_data'])}")
        else:
            st.dataframe(st.session_state['data'].head(20))
            st.download_button("Download CSV", clean_and_export_data(st.session_state['data']), file_name="leads.csv", mime="text/csv")
            st.write(f"Total results: {len(st.session_state['data'])}") 