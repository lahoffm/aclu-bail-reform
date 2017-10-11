# Main webscraper script
# As of Oct 2017, http://www.henrycountysheriff.net/robots.txt does not exist
from scraper_henry import ScraperHenry
import time

# helpful to view ac.df long strings: pd.options.display.max_colwidth = 50

t = time.time()

ac = ScraperHenry(timeout=10, retries=3, sleep_sec=1)
ac.scrape_all()

elapsed = round(time.time() - t)
print('Seconds elapsed: ' + str(elapsed) + ', minutes elapsed: ' + str(elapsed/60))
