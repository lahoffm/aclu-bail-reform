# Webscraper for Muscogee county

- python 3.6.3
- Retrieves records for [Muscogee County Jail](https://www.columbusga.org/sheriff/InmateSearch.htm)
- prerequisites:

# Prerequisites to run

Have beautiful soup and selenium installed.  On Windows with Python 3.6 installed and added to PATH, install them with these commands:
```
pip install selenium
pip install beautifulsoup4
```

You also need to download the Chromedriver and copy its system path.
To download chromedriver.exe go to this address: https://sites.google.com/a/chromium.org/chromedriver/downloads
I am using v2.33.
Extract the zipped file anywhere you want to keep it and copy the path (shift+right-click >> "Copy as Path"). Add the path to the script inside the "chrome_path" variable.  
```
chrome_path = r""
```

# Running the program

- Just run `python webscraper.py`