# Webscraper for Athens-Clarke county, GA

from bs4 import BeautifulSoup # beautifulsoup4
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Webscrapes a single page and dumps to MySQL database
class Scraper(object):
    def __init__(self, url, timeout=10): # timeout = seconds timeout to avoid infinite waiting
        self.url = url
        self.timeout = timeout
    def scrape(self):
        self.response = requests.get(self.url, timeout=self.timeout)
        if response.status_code != requests.codes.ok:
            raise ValueError('Invalid http response code') # TODO make this an exception from Requests library
        self.html = response.text
        self.headers = response.headers
        #with open('test.html', 'w') as f:
        #    f.write(html)
    def dump(self): # dump to database
        print('test')


#athensclarke = Scraper("http://enigma.athensclarkecounty.com/photo/jailcurrent.asp")
#athensclarke.scrape()
#athensclarke.dump()

# 'mysql+mysqlconnector://user:pass@host/db'
conn = create_engine('mysql+mysqlconnector://root:password@localhost:3306/ap') 
result = conn.execute('INSERT INTO terms VALUES (1, "testing", 110);')
    
result = conn.execute('SELECT * FROM terms')

for row in result:
    print(row)
