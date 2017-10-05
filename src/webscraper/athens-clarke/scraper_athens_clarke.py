import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

class ScraperAthensClarke(object):
    """Webscraper for Athens-Clarke county jail, GA"""
       
    def __init__(self, url, timeout=10):
        self.url = url # entry URL from which to start scraping
        self.timeout = timeout # seconds timeout to avoid infinite waiting

    def get_page(self, url):
        """Get html for a single page."""
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != requests.codes.ok:
            raise requests.HTTPError('HTTP response code was {0}, should have been {1}'.format(response.status_code, requests.codes.ok))
        return response.text
    
    def scrape_main(self):
        """Get main page table into data frame formatted for the output CSV"""
        
        # Get main page table into data frame
        self.html_main = self.get_page(self.url) # will be used to get subpage links
        df_list = pd.read_html(self.html_main, header=0, converters={'MID#': str,
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
        assert len(df_list) == 1, 'Should be only 1 table on page'
        df_main = df_list[0] 
        df_main = df_main.iloc[1:,:] # drop 1st row, it's all NaN because site had an extra TR tag.
        df_main.reset_index(drop=True, inplace=True) # so indexes equal to self.df indexes
        assert all(df_main.columns==['MID#', 'NAME', 'SEX', 'RACE', 'BOOKING DATE', 'CHARGE', 'BOND AMOUNT', 'CASE NUMBER', 'POLICE CASE#', 'YEAR OF BIRTH', 'VISITATION']), 'Column names have changed'

        # This will go in CSV file.
        self.df = pd.DataFrame(np.zeros((df_main.shape[0], 25)), columns=[
                  'county_name', # yes
                  'timestamp', # yes - time subpage was accessed (if couldn't connect, it's the main page timestamp)
                  'url', # yes - subpage urls (if couldn't connect, it's the main page url)
                  'inmate_id', # yes
                  'inmate_lastname', # yes
                  'inmate_firstname', # yes
                  'inmate_middlename', # yes
                  'inmate_sex', # yes
                  'inmate_race', # yes
                  'inmate_age', # yes - the age they turn on their birthdays in current year
                  'inmate_dob', # yes - only the year
                  'inmate_address',
                  'booking_timestamp', # yes
                  'release_timestamp',
                  'processing_numbers', # yes
                  'agency',
                  'facility',
                  'charges',
                  'severity',
                  'bond_amount',
                  'current_status',
                  'court_dates',
                  'days_jailed',
                  'other',
                  'notes'])
        self.df[:] = '' # unfilled columns will be written to CSV as empty strings

        # Set county name, timestamp, url
        # url will be overwritten with subpage's url unless we get HTTP errors
        # timestamp will be overwritten with subpage's timestamp unless we get HTTP errors
        self.df.county_name = 'athens-clarke'
        self.df.url = self.url
        self.df.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')  # hardcoded EST because it's not critical to get the hour correct,
                                                                              # timestamps are just for knowing roughly when we scraped.

        # Set inmate ID
        assert all(pd.notnull(df_main['MID#']))
        self.df['inmate_id'] = df_main['MID#']
          
        # Set inmate last/first/middle name. Assumes format is "lastname, firstname zero or more middle names"
        assert all(pd.notnull(df_main['NAME']))
        inmate_name = df_main['NAME'].str.split(', ', n=1, expand=True)
        assert inmate_name.shape[1] == 2, 'Invalid name format'
        self.df['inmate_lastname'] = inmate_name.iloc[:,0]
        inmate_name = inmate_name.iloc[:,1]
        inmate_name = inmate_name.str.split(' ', n=1, expand=True)
        assert inmate_name.shape[1] == 2, 'Invalid name format'
        inmate_name.fillna('', inplace=True)
        self.df['inmate_firstname'] = inmate_name.iloc[:,0]
        self.df['inmate_middlename'] = inmate_name.iloc[:,1]
        
        # Set inmate sex
        assert all(pd.notnull(df_main['SEX']))
        assert np.isin(df_main['SEX'].unique(), np.array(['MALE','FEMALE'])).all(), "Invalid sex format"
        self.df['inmate_sex'] = df_main['SEX'].str.lower().str[0]
        
        # Set inmate race
        assert all(pd.notnull(df_main['RACE']))
        inmate_race = df_main['RACE'].str.lower() # don't have to convert 'asian' or 'white' because already listed that way
        inmate_race = inmate_race.str.replace('black/african american', 'black')
        inmate_race = inmate_race.str.replace('hispanic or latino', 'hispanic')
        inmate_race = inmate_race.str.replace('middle eastern decent', 'middle-eastern') # they had a typo
        assert np.isin(inmate_race.unique(), np.array(['asian','white','black','hispanic','middle-eastern'])).all(),\
                     "One or more of these races not converted to standard format: " + str(inmate_race.unique())
        self.df['inmate_race'] = inmate_race
        
        # Set booking timestamp
        # Hardcoding 'EST' because Athens-Clarke county is in Georgia USA
        # See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        # Outputs 'YYYY-MM-DD HH:MM:SS EST', see https://docs.python.org/3/library/datetime.html#datetime.datetime.__str__             
        assert all(pd.notnull(df_main['BOOKING DATE']))
        convert_dt = lambda dt : str(datetime.strptime(dt, "%m/%d/%Y %I:%M:%S %p")) + ' EST' # Format changes will likely be caught here
        self.df['booking_timestamp'] = df_main['BOOKING DATE'].apply(convert_dt)
        
        # Not setting charges or bond_amount from main page, because more detailed info found in subpages

        # Set case number - many are blank for Athens-Clarke county
        # Replace semicolons so ETL code doesn't think they are multiple processing numbers
        # Format is 'Case # XXX;Police case # XXX'. If one or both are missing there is still a ';'
        #   so ETL parser knows what's missing.
        self.df['processing_numbers'] = 'Case # ' + df_main['CASE NUMBER'].str.replace(';',':')
        self.df['processing_numbers'].fillna('', inplace=True)
        tmp = ';Police case # ' + df_main['POLICE CASE#'].str.replace(';',':')
        tmp.fillna(';', inplace=True)
        self.df['processing_numbers'] = self.df['processing_numbers'].str.cat(tmp)
        
        # Set inmate date of birth - only the year is available for Athens-Clarke county
        assert all(pd.notnull(df_main['YEAR OF BIRTH']))
        assert all(df_main['YEAR OF BIRTH'].str.len()==4), 'Invalid year of birth format'
        self.df['inmate_dob'] = df_main['YEAR OF BIRTH']
        
        # Set inmate age when we scraped the site
        # Because we only have birth year, age is whatever age they turn on their birthdays in the current year.
        # That means it's impossible for 18 year olds (minimum booking age) to be incorrectly assigned age 17.
        calc_age = lambda yyyy : str(datetime.now().year - int(yyyy))
        self.df['inmate_age'] = df_main['YEAR OF BIRTH'].apply(calc_age)
        
    def scrape_sub(self, url):
        print('scrape sub')
        """
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
        
        """
        
    def scrape_all(self):
        """ Scrape main page then each inmate's subpage with more details.
            Assemble results into pandas dataframe in standard format and dump to CSV file."""
        self.scrape_main()
        self.dump()

    
    def dump(self):
        self.df.iloc[1,0:10] = ['Spa, m', 'test\ntest', "Lovely ,,,Spam", None, 'test:',   'Wond"""""erful "haha" ""! ; test ;Spam', 'tes"t', 'test', None, None]
        
        csv_fname = datetime.now().strftime('athens-clarke_current-inmate-roster_%Y_%m_%d_%H_%M_%S.csv')
        csv_dir = '../../../data'
        self.df.to_csv(csv_dir + '/' + csv_fname, index=False, line_terminator='\n') # matches default params for csv.writer
        print('Wrote ' + csv_fname + ' to ' + csv_dir)