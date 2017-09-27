import requests

class Scraper(object):
    """Webscraper superclass. Subclasses must implement scrape_all
       because each county jail has different data access format"""
       
    def __init__(self, url, engine, timeout=10):
        self.url = url # entry URL from which to start scraping
        self.timeout = timeout # seconds timeout to avoid infinite waiting
        self.engine = engine # database
        
    def scrape(self, url): # Scrape a single page. Should be called by scrape_all for each page of interest
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != requests.codes.ok:
            raise ValueError('Invalid http response code') # TODO replace with better error type
        html = response.text
        headers = response.headers
        print(headers)
        
    def scrape_all(self):
        raise NotImplementedError("Subclass must implement method scrape_all to scrape the county-specific jail data format")
        
    def dump(self): # Dump one or more pages to database
        print('test')
        connection = self.engine.connect()
        result = connection.execute('SELECT * FROM terms')
        for row in result:
            print(row)

        connection.close()
    