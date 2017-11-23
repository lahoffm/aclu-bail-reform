# Fulton County Jail Webscraper

This code was written in **Python 3.6**, and relies on **selenium** and **BeautifulSoup4**.
Both of these packages can installed via `pip install -r requirements.txt`.

The script `get_new_books.py` is run regularly to get new bookings that have been added to the Fulton County Jail website. It marks its progress by updating the `last_record.txt` log file on each run. It also adds to the `unreleased.txt` logfile on each run, adding the booking number of any booking that does not show a release date at the time of scraping.

The script `update_old_books.py` can be run to check for changes to the bookings listed in `unreleased.txt`. It produces a csv file of the same format as the regular script. If a booking is found to have a release date, it is removed from the `unreleased.txt` file.

The csv files produced by both scripts conform with the specification in `contributing.md`, and use the `other` column to store a pipe-separated list of the offense date (which can be several years before the booking date in the case of people who are arrested on warrants, which I think will be an interesting dimension to look into).

If you are using Chrome on Windows, the selenium driver `chromedriver.exe` has already been placed in this directory.
It runs **ChromeDriver 2.33**, which supports Chrome v60-62 according to selenium docs.

Otherwise, selenium will require that a driver be placed in this directory. See [link](http://selenium-python.readthedocs.io/installation.html) for details.

Following lines of `get_new_books.py` and `update_old_books.py` will need adjustment if using a setup other than Chrome on Windows.
```python
chrome_path = os.path.join(dir_path,"chromedriver")
driver = webdriver.Chrome(chrome_path)
```
