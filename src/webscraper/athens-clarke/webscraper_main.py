# Main webscraper script
from scraper_athens_clarke import ScraperAthensClarke
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

athensclarke = ScraperAthensClarke(url="http://enigma.athensclarkecounty.com/photo/jailcurrent.asp", timeout=10)
html, df_main, soup, html_sub, df_sub1, df_sub2 = athensclarke.scrape_all()

df = pd.DataFrame(np.zeros((df_main.shape[0], 24)), columns=[
                  'county_name',
                  'timestamp',
                  'url',
                  'inmate_id', # yes
                  'inmate_lastname', # yes
                  'inmate_firstname', # yes
                  'inmate_middlename', # yes
                  'inmate_sex', # yes
                  'inmate_race',
                  'inmate_age',
                  'inmate_dob',
                  'inmate_address',
                  'booking_timestamp',
                  'release_timestamp',
                  'processing_numbers',
                  'agency',
                  'facility',
                  'charges',
                  'severity',
                  'bond_amount',
                  'current_status',
                  'court_dates',
                  'days_jailed',
                  'other'])
df[:] = '' # unfilled columns will be written to CSV as empty strings

# Set columns to be saved to CSV, that are obtainable from main page
df['inmate_id'] = df_main['MID#']

inmate_name = df_main['NAME'].str.split(', ', n=1, expand=True)
df['inmate_lastname'] = inmate_name.iloc[:,0]
inmate_name = inmate_name.iloc[:,1]
inmate_name = inmate_name.str.split(' ', n=1, expand=True)
inmate_name.fillna('', inplace=True)
df['inmate_firstname'] = inmate_name.iloc[:,0]
df['inmate_middlename'] = inmate_name.iloc[:,1]

df['inmate_sex'] = df_main['SEX'].str.lower().str[0]

inmate_race = df_main['RACE'].str.lower() # don't have to convert 'white' or 'asian' because already listed that way
inmate_race = inmate_race.str.replace('black/african american', 'black')
inmate_race = inmate_race.str.replace('hispanic or latino', 'hispanic')
inmate_race = inmate_race.str.replace('middle eastern decent', 'middle-eastern')
assert np.isin(inmate_race.unique(), np.array(['black','white','hispanic','asian','middle-eastern', np.nan])).all(), "One or more races not converted to standard format" # make sure we didn't miss specifying a race

print(df.head(5));print(df_main.head(5));print(df.tail(5));print(df_main.tail(5))


s = df['col'].str.replace('old', 'new')


#id_ = 1
#with open('{}.html'.format(id_), 'w') as f:
#    f.write(html_sub)
# test csv writer
#import csv
#with open('test.csv', 'w', newline='') as csvfile:
#    writer = csv.writer(csvfile)
#    writer.writerow(['Spam'] * 5 + ['Baked Beans'])
#    writer.writerow(['Spa, m', 'test\ntest', "Lovely ,,,Spam", None, 'test:',   'Wond"""""erful "haha" ""! ; test ;Spam', 'tes"t', 'test', None, None])



#http://enigma.athensclarkecounty.com/photo/detailsNEW.asp?id=-97099&bid=2017-00005779&pg=1&curr=yes
#                                           detailsNEW.asp?id=-97099&bid=2017-00005779&pg=1&curr=yes

"""
# This should all go to etl code later, doesn't belong in webscraper

# Must have 3 command line args!
import sys
from sqlalchemy import create_engine
user     = sys.argv[1] # MySql username
password = sys.argv[2] # MySql password
host     = sys.argv[3] # MySql host & port like localhost:3306
database = 'jaildata'
timeout  = 15

engine = create_engine("mysql+mysqlconnector://" + user + ":" + password + "@" + host + "/" + database) 

    def dump(self): # Dump one or more pages to database
        print('test')
        connection = self.engine.connect()
        result = connection.execute('SELECT * FROM terms')
        for row in result:
            print(row)

        connection.close()
"""
