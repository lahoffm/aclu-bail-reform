# Main webscraper script
# As of Oct 2017, https://www.athensclarkecounty.com/robots.txt did not disallow what we are scraping
from scraper_athens_clarke import ScraperAthensClarke
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime

athensclarke = ScraperAthensClarke(url="http://enigma.athensclarkecounty.com/photo/jailcurrent.asp", timeout=10)
athensclarke.scrape_all()

def v(my_df):
    print(my_df.head(5))
    print(my_df.tail(5))

def c(my_df, col):
    print(my_df[col].head(5))
    print(my_df[col].tail(5))

df = athensclarke.df