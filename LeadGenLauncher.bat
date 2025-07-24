@echo off
REM Change directory to the project folder
cd /d "%~dp0"

REM Install requirements only once
if not exist .requirements_installed (
    pip install -r requirements.txt
    echo done > .requirements_installed
)

REM Run the Streamlit app
streamlit run app.py

pause 