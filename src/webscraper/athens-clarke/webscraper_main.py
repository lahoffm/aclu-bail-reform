# Main webscraper script
# As of Oct 2017, https://www.athensclarkecounty.com/robots.txt did not disallow what we are scraping
from scraper_athens_clarke import ScraperAthensClarke
import time

# helpful to view ac.df long strings: pd.options.display.max_colwidth = 50

t = time.time()

ac = ScraperAthensClarke(timeout=10, retries=3, sleep_sec=1)
ac.scrape_all()

elapsed = round(time.time() - t)
print('Seconds elapsed: ' + str(elapsed) + ', minutes elapsed: ' + str(elapsed/60))
