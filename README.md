# Assignment Dashboard

A personal dashboard that pulls your upcoming assignments from **Gradescope** and **Canvas** and displays them in one place, sorted by due date.


## Requirements

- A computer running Windows, Mac, or Linux
- An internet connection
- A Gradescope account and a Canvas account


## Step 1 — Install Python

1. Go to **https://www.python.org/downloads**
2. Click the big yellow "Download Python" button
3. Run the installer
   - **Windows:** check the box that says **"Add Python to PATH"** before clicking Install
   - **Mac/Linux:** the defaults are fine
4. Verify it worked by opening a terminal and running:
```
   python --version
```
   You should see something like `Python 3.12.0`


## Step 2 — Download this project

If you have Git installed:

git clone https://github.com/poolapp13/Assignment-Dashboard
cd Assignment-Dashboard


OR click the green **Code** button on GitHub and select **Download ZIP**, then extract it.



## Step 3 — Install dependencies

Open a terminal inside the project folder and run:
```
pip install -r requirements.txt
playwright install chromium
```

This installs all the required libraries and downloads the browser Playwright uses. It may take a few minutes.



## Step 4 — Run setup

```
python setup.py
```

This will:
1. Ask for your Canvas URL (e.g. `canvas.university.edu`)
2. Open a browser window for you to log into Gradescope
3. Open a browser window for you to log into Canvas
4. Show you all your courses and let you remove any you don't want to track
5. Save everything to a `config.json` file

You only need to run setup once (or again if your courses change each semester).



## Step 5 — Fetch your assignments

```
python scraper.py
```
This opens your Gradescope and Canvas, scrapes all upcoming unsubmitted assignments, and saves them to `assignments.json`.



## Step 6 — View the dashboard

Start the local server:
```
python -m http.server
```

Then open your browser and go to:

http://localhost:8000/dashboard.html


You'll see all your upcoming assignments sorted by due date with color-coded urgency.



## Daily workflow

Whenever you want to update your assignments:

1. Run `python scraper.py`
2. Run `python -m http.server`
3. Open `http://localhost:8000/dashboard.html`



## Troubleshooting

**"python is not recognized"**
- Make sure you checked "Add Python to PATH" during installation
- Try restarting your terminal

**"Could not load assignments.json"**
- Make sure you ran `python scraper.py` first
- Make sure `python -m http.server` is running in the same folder as `dashboard.html`

**Dashboard shows old assignments**
- Re-run `python scraper.py` to refresh the data, then reload the page

**Session expired / scraper opens login page**
- Delete `session.json` and/or `canvas_session.json` and re-run `python scraper.py` — it will prompt you to log in again



## Privacy

- Your login sessions are stored locally in `session.json` and `canvas_session.json`
- These files are in `.gitignore` and will never be uploaded to GitHub
- Your assignment data is stored locally in `assignments.json`, also ignored by Git
- Nothing is sent to any external server
