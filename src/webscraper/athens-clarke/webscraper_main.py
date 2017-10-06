# Main webscraper script
# As of Oct 2017, https://www.athensclarkecounty.com/robots.txt did not disallow what we are scraping
from scraper_athens_clarke import ScraperAthensClarke
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime
import time

t = time.time()
athensclarke = ScraperAthensClarke(timeout=10, retries=3, sleep_sec=0)
athensclarke.scrape_all()
df = athensclarke.df

elapsed = round(time.time() - t)

print('Seconds elapsed: ' + str(elapsed) + ', minutes elapsed: ' + str(elapsed/60))
def v(my_df):
    print(my_df.head(5))
    print(my_df.tail(5))
def c(my_df, col):
    print(my_df[col].head(5))
    print(my_df[col].tail(5))
