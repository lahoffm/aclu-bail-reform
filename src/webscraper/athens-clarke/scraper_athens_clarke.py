import requests
import csv
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

class ScraperAthensClarke(object):
    """Webscraper for Athens-Clarke county jail, GA"""
       
    def __init__(self, url, timeout=10):
        self.url = url # entry URL from which to start scraping
        self.timeout = timeout # seconds timeout to avoid infinite waiting
        
    def get_page(self, url): # Get html and headers for a single page.
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != requests.codes.ok:
            raise requests.HTTPError('HTTP response code was {0}, should have been {1}'.format(response.status_code, requests.codes.ok))
        return response.text
    
    def scrape_all(self):
        
        # Get main page table into data frame
        html = self.get_page(self.url)
        df_list = pd.read_html(html, header=0, converters={'MID#': str,
                                                           'NAME': str,
                                                           'SEX': str,
                                                           'RACE': str,
                                                           'BOOKING DATE': str,
                                                           'CHARGE': str,
                                                           'BOND AMOUNT': str,
                                                           'CASE NUMBER': str,
                                                           'POLICE CASE#': str,
                                                           'YEAR OF BIRTH': str,
                                                           'VISITATION': str})
        assert len(df_list) == 1, '<>1 table on page.'
        df_main = df_list[0] 
        df_main = df_main.iloc[1:,:] # drop 1st row, it's all NaN because site had an extra TR tag.
        df_main.reset_index(drop=True, inplace=True) 
        
        soup = BeautifulSoup(html, 'lxml')
        i = 0
        
        for a in soup.find_all('a', href=True):
            
            # Get subpage's 2 tables into list of data frames
            print('Downloading subpage {0} of {1}...'.format(i+1, df_main.shape[0]))
            subpage = self.url[0:self.url.rfind('/')+1] + a["onclick"].split(',')[0].split("'")[1]
            html_sub = self.get_page(subpage)
            df_list = pd.read_html(html_sub, match="Name:", converters={0: str, 1: str, 2: str, 3: str})
            assert len(df_list) == 1, "<>1 table on page with matching text."
            df_sub1 = df_list[0]
            df_list = pd.read_html(html_sub, header=0, match="ARRESTING AGENCY", converters={0: str, 1: str, 2: str, 3: str, 4: str, 5: str, 6: str})
            assert len(df_list) == 1, "<>1 table on page with matching text."
            df_sub2 = df_list[0]
            i = i + 1
            if i==2:
                break
        #assert i == df.shape[0], "Number of hrefs not equal to number of names"
        
        return html, df_main, soup, html_sub, df_sub1, df_sub2
    
    def dump(self, df): # Dump pandas dataframe to CSV. All subclasses should call this at the end of scrape_all.
        print(df)
        