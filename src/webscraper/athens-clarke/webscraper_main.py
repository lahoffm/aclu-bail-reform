# Main webscraper script
from scraper_athensclarke import ScraperAthensClarke
import sys
from sqlalchemy import create_engine
from csv import writer

print('test')


"""
# Must have 3 command line args!
user     = sys.argv[1] # MySql username
password = sys.argv[2] # MySql password
host     = sys.argv[3] # MySql host & port like localhost:3306
database = 'jaildata'
timeout  = 15

engine = create_engine("mysql+mysqlconnector://" + user + ":" + password + "@" + host + "/" + database) 

athensclarke = ScraperAthensClarke("http://enigma.athensclarkecounty.com/photo/jailcurrent.asp", engine, timeout)
athensclarke.scrape_all()
athensclarke.dump()
"""