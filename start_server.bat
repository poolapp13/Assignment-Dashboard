@echo off
cd C:\Users\jiemi\Python\Assignment-Dashboard
python scraper.py
start /min python -m http.server
