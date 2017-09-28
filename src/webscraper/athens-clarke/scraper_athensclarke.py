from scraper import Scraper

class ScraperAthensClarke(Scraper):
    """Webscraper for Athens-Clarke county, GA"""
    
    def scrape_all(self):
        self.scrape(self.url)