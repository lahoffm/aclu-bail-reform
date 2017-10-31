import requests
import numpy as np
import pandas as pd
import time
from warnings import warn
from bs4 import BeautifulSoup
from datetime import datetime

class ScraperAthensClarke(object):
    """Webscraper for Athens-Clarke county jail, GA
        This county has 2 main sites to scrape: their current inmate roster
        and their arrests from the last 7 days (booking report).
        They offer similar information, but the booking report also shows released
        inmates, whether they posted bail / time served / recognizance / etc.,
        court jurisdiction and warrant #s. Best to make 2 CSV files so we can
        use the two info sources in different ways.
    """    
    
    def __init__(self, timeout=10, retries=0, sleep_sec=5):
        self.url_roster = "http://enigma.athensclarkecounty.com/photo/jailcurrent.asp" # entry URL from which to start scraping current inmate roster
        self.url_booking = "http://enigma.athensclarkecounty.com/photo/bookingreport.asp" # entry URL from which to start scraping "arrests from last 7 days"
        self.timeout = timeout # seconds timeout to avoid infinite waiting
        self.retries = retries # how many times to retry loading if there's http errors.
        self.sleep_sec = sleep_sec # seconds to wait between subpage requests to avoid overloading server
        response = requests.head(url=self.url_roster) # set user-agent so they can contact us if they don't like how we're scraping
        self.headers = {'User-Agent' : response.request.headers['User-Agent'] + ' (Contact lahoffm@gmail.com, https://github.com/lahoffm/aclu-bail-reform)'}
        self.csv_dir = '../../../data' # where to write data
        self.df = [] # will be a dataframe later. self.df is created for inmate roster, dumped to file, recreated for booking report, dumped to file
        self.multi_booking_str = 'Inmate booked >1 times over last 7 days. Kept only most recent booking timestamp. Because of this, multiple subpages for this inmate, but only saved data for one subpage. Consider ignoring this datapoint.'
        
        
    def scrape_all(self):
        """ Scrape main page then each inmate's subpage with more details.
            Assemble results into pandas dataframe in standard format and dump to CSV file."""
            
        html_main = self.scrape_main_roster() # current inmate roster
        self.scrape_sub(html_main, 'roster')
        self.dump('current-inmate-roster')
        
        html_main = self.scrape_main_booking() # recent bookings ("arrests last 7 days")
        self.scrape_sub(html_main, 'booking')
        self.dump('booking-report')



    def scrape_main_roster(self):
        """Get main inmate roster table into data frame formatted for the output CSV"""
        
        # Get main page table into data frame
        html_main, errormsg = self.get_page(self.url_roster) # will be used to get subpage links
        if errormsg is not None:
            raise requests.RequestException('Could not get main jail page. Error message: ' + errormsg)
        df_list = pd.read_html(html_main, header=0, converters={'MID#': str,
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
        self.init_df(df_main.shape[0]) # init self.df
        
        # Set URL - will be overwritten with subpage's url unless we get HTTP errors
        self.df['url'] = self.url_roster
                
        # Set inmate ID
        assert all(pd.notnull(df_main['MID#']))
        assert df_main['MID#'].nunique() == df_main.shape[0], 'Non-unique inmate IDs' # check inmate IDs are unique so matching works in scrape_sub
        self.df['inmate_id'] = df_main['MID#']

        # Set inmate last/first/middle name.
        self.set_inmate_name(df_main)
        
        # Set inmate sex
        self.set_inmate_sex(df_main)
        
        # Set inmate race
        self.set_inmate_race(df_main)
        
        # Set booking timestamp
        self.set_booking_timestamp(df_main, 'BOOKING DATE')
        
        # Not setting charges or bond_amount from main page, because more detailed info found in subpages

        # Set case number - many are blank for Athens-Clarke county
        # Replace semicolons so ETL code doesn't think they are multiple processing numbers
        # Format is 'Case # XXX | Police case # XXX'. If one or both are missing there is still a ' | '
        #   so ETL parser knows what's missing.
        self.df['processing_numbers'] = 'Case # ' + df_main['CASE NUMBER'].str.replace('|',':')
        self.df['processing_numbers'].fillna('', inplace=True)
        tmp = ' | Police case # ' + df_main['POLICE CASE#'].str.replace('|',':')
        tmp.fillna(' | ', inplace=True)
        self.df['processing_numbers'] = self.df['processing_numbers'].str.cat(tmp)
        
        # Set inmate date of birth - only the year is available for Athens-Clarke county
        self.set_inmate_dob(df_main)
        
        # Set inmate age when we scraped the site
        self.set_inmate_age(df_main)
        
        return html_main
        
    
    
    def scrape_main_booking(self):
        """ Get main inmate booking table into data frame formatted for the output CSV.
            NB in contrast to scrape_main_roster, we have to do some split/apply/combine
            at the end, because inmates have one row per charge on the main page.
            What we want is to get one row per inmate. """

        # Get main page table into data frame
        html_main, errormsg = self.get_page(self.url_booking) # will be used to get subpage links
        if errormsg is not None:
            raise requests.RequestException('Could not get main jail page. Error message: ' + errormsg)
        df_list = pd.read_html(html_main, header=0, converters={'MID#': str,
                                                           'BOOKING TIME': str,
                                                           'NAME': str,
                                                           'YEAR OF BIRTH': str,
                                                           'RACE': str,
                                                           'SEX': str,
                                                           'ARRESTING AGENCY': str,
                                                           'RELEASE TIME': str,
                                                           'CHARGE': str,
                                                           'CRIME TYPE': str,
                                                           'COURT JURISDICTION': str,
                                                           'BONDING COMPANY': str,
                                                           'BOND AMOUNT': str,
                                                           'WARRANT #': str,
                                                           'POLICE CASE#': str})
        assert len(df_list) == 1, 'Should be only 1 table on page'
        df_main = df_list[0]  # Unlike for roster, don't have to drop 1st row
        assert all(df_main.columns==['MID#', 'BOOKING TIME', 'NAME', 'YEAR OF BIRTH', 'RACE', 'SEX', 'ARRESTING AGENCY', 'RELEASE TIME', 'CHARGE', 'CRIME TYPE', 'COURT JURISDICTION', 'BONDING COMPANY', 'BOND AMOUNT', 'WARRANT #', 'POLICE CASE#']), 'Column names have changed'
        self.init_df(df_main.shape[0]) # init self.df - final nrows will be smaller because of split/apply/combine later
        
        # Set URL - will be overwritten with subpage's url unless we get HTTP errors
        self.df['url'] = self.url_booking

        # Set inmate ID --> the main booking page MID# differs from inmate detail page MID#, so this will be overwritten
        # when scraping subpages. Will ultimately save subpage MID# because this is consistent with how "current roster"
        # page does it. We need the main page MID# in this function to do split/apply/combine by inmate.
        assert all(pd.notnull(df_main['MID#'])) # Unlike for roster, not checking inmate IDs are unique
        self.df['inmate_id'] = df_main['MID#']

        # Set booking timestamp
        self.set_booking_timestamp(df_main, 'BOOKING TIME')
        
        # Set inmate last/first/middle name.
        self.set_inmate_name(df_main)
    
        # Set inmate date of birth - only the year is available for Athens-Clarke county
        self.set_inmate_dob(df_main)

        # Set inmate race
        self.set_inmate_race(df_main)
            
        # Set inmate sex
        self.set_inmate_sex(df_main)
        
        # Set arresting agency
        assert all(pd.notnull(df_main['ARRESTING AGENCY'])) 
        self.df['agency'] = df_main['ARRESTING AGENCY']
        
        # Set release timestamp - county has different format than booking times
        # See set_booking_timestamp() for more comments
        df_main['RELEASE TIME'].fillna('', inplace=True)
        convert_dt = lambda dt : '' if dt=='' else (str(datetime.strptime(dt, "%m/%d/%Y %I:%M%p")) + ' EST') # Format changes will likely be caught here
        self.df['release_timestamp'] = df_main["RELEASE TIME"].apply(convert_dt)
    
        # Set charge - at present, there's 1 row per charge but will split/apply/combine later so it's 1 row per inmate
        df_main['CHARGE'].fillna('', inplace=True) # this happens sometimes, probably as they are in process of updating a person's charge
        self.df['charges'] = df_main['CHARGE'].str.replace('|',':') # convert so we can later chain charges with ' | '
    
        # Set charge severity - ignoring "Local ordinance" because it's rare
        df_main.fillna('', inplace=True) # all columns from this point forward probably have NaN so fill with ''
        df_main['CRIME TYPE'] = df_main['CRIME TYPE'].str.lower().str.replace('local ordinance','')
        assert np.isin(df_main['CRIME TYPE'].unique(), np.array(['misdemeanor','felony',''])).all(), 'Invalid misdemeanor/felony format.'                                       
        self.df['severity'] = df_main['CRIME TYPE']
        
        # Set court jurisdiction in 'other' field
        self.df['other'] = pd.Series(['Court jurisdiction: ']*df_main.shape[0]).str.cat(df_main['COURT JURISDICTION'].str.replace('|',':'))
        self.df.loc[self.df['other']=='Court jurisdiction: ','other'] = ''
        
        # Set bond_amount - will add to this when scraping subpages
        self.format_bond_amount(df_main)
        df_main['BONDING COMPANY'] = df_main['BONDING COMPANY'].str.replace('|',':')
        self.df['bond_amount'] = df_main['BOND AMOUNT'].str.cat([["( Bonding company:"]*df_main.shape[0],\
                                                             df_main['BONDING COMPANY'],\
                                                             [')']*df_main.shape[0]],\
                                                             sep=' ')

        # Set case number & warrant number - see comments in scrape_main_roster()
        self.df['processing_numbers'] = 'Warrant # ' + df_main['WARRANT #'].str.replace('|',':')
        self.df.loc[self.df['processing_numbers']=='Warrant # ','processing_numbers'] = ''
        tmp = ',Police case # ' + df_main['POLICE CASE#'].str.replace('|',':')
        tmp[tmp==',Police case # '] = ',' # split with ',' instead of ' | ' because each charge has its own warrant/case#
        self.df['processing_numbers'] = self.df['processing_numbers'].str.cat(tmp)
   
        # Set inmate age when we scraped the site
        self.set_inmate_age(df_main)
        
        # Split/apply/combine
        # On the main booking site they post multiple rows per inmate, one row per charge.
        # This code compresses it into one row per inmate, as required for the csv specification
        inmate_groups = self.df.groupby('inmate_id', sort=False, as_index=False) # each group = 1 inmate
        self.df = inmate_groups.apply(self.compress_inmate_rows) # now each inmate (technically, each inmate_id) has one row with 1+ charges, etc.
        self.df.reset_index(drop=True, inplace=True) # apply() returns it with multiindex we don't need

        return html_main
    
    
    
    def scrape_sub(self, html_main, flag):
        """ Scrape each inmate's details page - links from main page.
            Add data to the inmate's row in self.df.
            Retry self.retries times if there's any errors, then skip to next
            subpage. If subpage couldn't be loaded, log it in the "notes" field.

            flag: 'roster' or 'booking' to scrape differently based on what is on main page
        """
        soup = BeautifulSoup(html_main, 'lxml')
        nlinks = len(list(soup.find_all('a', href=True)))
        if flag=='roster':
            assert nlinks == self.df.shape[0], "Number of hrefs != number of table entries"
        else:
            self.df['inmate_id'] = ''  # The booking page MID# differs from inmate detail MID#. We will use the subpage MID# for consistency with "current roster" page
        
        self.df['notes'].fillna('Failed to load inmate detail page. Leaving some fields blank', inplace=True) # will be erased ONLY when page successfully loads
                                                                                                              # nb compress_inmate_rows may have set a couple 'notes' fields already
        
        i = 0
        for a in soup.find_all('a', href=True): # scrape each subpage (which have additional details for a single inmate)
            # Get subpage
            # The tag's format should be
            #      <a href="##" onclick="window.open('detailsNEW.asp?id=-59091&amp;bid=2017-00004550&amp;pg=1&amp;curr=yes',
            #      'search', 'width=730,height=800,status=yes,resizable=yes,scrollbars=yes')">ABOYADE, OLUFEMI BABALOLA</a>
            i = i + 1
            print('Downloading subpage {0} of {1} at {2}...'.format(i, nlinks, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            url_main = self.url_roster if flag=='roster' else self.url_booking
            subpage_url = url_main[0:url_main.rfind('/')+1] + a["onclick"].split(',')[0].split("'")[1]
            if any(self.df['url'].isin([subpage_url])): # already visited link - happens for booking site
                continue
            html_sub, errormsg = self.get_page(subpage_url)
            if errormsg is not None:
                warn('Could not get URL "' + subpage_url + '" for subpage ' + str(i) + '. Error message: ' + errormsg + '. Continuing to next page')
                continue
  
            # Get subpage's 2 tables in dataframes
            try:
                df_list = pd.read_html(html_sub, match="Name:", converters={0: str, 1: str, 2: str, 3: str})
            except ValueError as e:
                warn(str(e) +' for subpage ' + str(i) + ', continuing to next page.')
                continue
            assert len(df_list) == 1, "Should be only 1 table on page with matching text."
            df_sub1 = df_list[0]
            assert df_sub1.shape==(5,4), 'Wrong table dimensions'
            if pd.isnull(df_sub1.loc[1,1]): df_sub1.loc[1,1]='' # for blank addresses 
            if pd.isnull(df_sub1.loc[2,3]): df_sub1.loc[2,3]='' # for blank races
            assert df_sub1.iloc[0,0]=='Name:' and df_sub1.iloc[1,0]=='Address:' and df_sub1.iloc[2,0]=='Sex:'\
                and df_sub1.iloc[3,0]=='Year of Birth:' and df_sub1.iloc[4,0]=='Booking Date/Time:' and pd.notnull(df_sub1.iloc[:,1]).all()\
                and df_sub1.iloc[0,2].startswith('MID#: ') and pd.isnull(df_sub1.iloc[1,2]) and df_sub1.iloc[2,2]=='Race:'\
                and df_sub1.iloc[3,2]=='Height/Weight:' and df_sub1.iloc[4,2]=='Released Date/Time:' and pd.isnull(df_sub1.iloc[0,3])\
                and pd.isnull(df_sub1.iloc[1,3]) and pd.notnull(df_sub1.iloc[2:5,3]).all(), 'Table format has changed'
            df_list = pd.read_html(html_sub, header=0, match="ARRESTING AGENCY", converters={0: str, 1: str, 2: str, 3: str, 4: str, 5: str, 6: str})
            assert len(df_list) == 1, "Should be only 1 table on page with matching text."
            df_sub2 = df_list[0]
            assert all(df_sub2.columns==['ARRESTING AGENCY', 'GRADE OF CHARGE', 'CHARGE DESCRIPTION', 'BOND AMOUNT', 'BOND REMARKS', 'BOND LAST UPDATED', 'DISPOSITION']), 'Column names have changed'
            assert not df_sub2.empty, 'Table has zero rows'
            
            # Find matching self.df row where we will insert data
            inmate_id = df_sub1.iloc[0,2][6:] # checked above that it starts with 'MID#: '           
            if flag=='roster':  # Use inmate id to match
                  ix = self.df.index[self.df['inmate_id']==inmate_id] # scrape_main_roster checked that inmate IDs are all unique, so this will match 1 row
                  assert not self.df.loc[ix].empty, 'Inmate id "' + inmate_id + '" not found in main page'
            else: # The booking page MID# differs from inmate detail MID#, so we have to match inmates other way
                inmate_name = df_sub1.iloc[0,1]
                booking_timestamp = self.convert_dt(df_sub1.iloc[4,1])
                inmate_names = self.df['inmate_lastname'].str.cat([[', ']*self.df.shape[0], \
                               self.df['inmate_firstname'], [' ']*self.df.shape[0], self.df['inmate_middlename']]).str.rstrip()
                tmp = pd.DataFrame({'inmate_name':inmate_names,'booking_timestamp':self.df['booking_timestamp']})
                ix = tmp.index[(tmp['inmate_name']==inmate_name) & (tmp['booking_timestamp']==booking_timestamp)]
                assert len(ix) == 1, 'Should be exactly one matching inmate in main page'


            # Set inmate ID
            if flag=='booking': # roster site has same inmate id on main page & subpage.
                # booking site's inmate ids differ on main page & subpages but to be consistent
                # with roster site, set it to subpage's inmate id.
                self.df.loc[ix,'inmate_id'] = inmate_id
                
            # Set URL
            self.df.loc[ix,'url'] = subpage_url
            
            # Set inmate address
            self.df.loc[ix, 'inmate_address'] = df_sub1.iloc[1,1]           

            # Set agency
            if flag=='roster': # booking site had this in main page
                assert all(pd.notnull(df_sub2['ARRESTING AGENCY'])), 'Invalid arresting agency format'
                try:
                    assert df_sub2['ARRESTING AGENCY'].nunique()==1, 'Invalid arresting agency format'
                except AssertionError as e:
                     warn(str(e) + ", multiple arresting agencies for subpage " + str(i) + ". Inserting the agency that made the arrest for each charge")
                     df_sub2.loc[0, 'ARRESTING AGENCY'] = df_sub2['ARRESTING AGENCY'].str.cat(sep=' | ')
                self.df.loc[ix, 'agency'] = df_sub2.loc[0, 'ARRESTING AGENCY']                                   
            
            df_sub2.fillna('', inplace=True) # important for later fields so semicolons go in right places
            
            # Set charge severity.
            # Sometimes one "grade of charge" is NaN, means they are holding the inmate for some other county.
            # We still put in the same fields, but the "grade of charge" will be an empty string.
            if flag=='roster': # booking site had this in main page
                if any(df_sub2['GRADE OF CHARGE'] == 'L'): # 'L' means 'Local ordinance' but this is rare so ignoring it
                    df_sub2['GRADE OF CHARGE'] = df_sub2['GRADE OF CHARGE'].str.replace('L','')
                    warn("Grade of charge 'L' (local ordinance) for subpage " + str(i) + ". Replacing with ''")
                assert np.isin(df_sub2['GRADE OF CHARGE'].unique(), np.array(['M','F',''])).all(), 'Invalid misdemeanor/felony format.'
                df_sub2['GRADE OF CHARGE'] = df_sub2['GRADE OF CHARGE'].str.replace('M','misdemeanor').str.replace('F','felony')
                self.df.loc[ix, 'severity'] = df_sub2['GRADE OF CHARGE'].str.cat(sep=' | ')

            # Set charges, separated by ' | ' even if charge description is empty string
            if flag=='roster': # booking site had this in main page
                self.df.loc[ix,'charges'] = df_sub2['CHARGE DESCRIPTION'].str.replace('|',':').str.cat(sep=' | ')

            # Set bond amount for each charge, separated by ' | '.
            if flag=='roster': # booking site had this in main page
                self.format_bond_amount(df_sub2)
                df_sub2['BOND REMARKS'] = df_sub2['BOND REMARKS'].str.replace('|',':')
                df_sub2['BOND LAST UPDATED'] = df_sub2['BOND LAST UPDATED'].str.replace('|',':')
                self.df.loc[ix,'bond_amount'] = df_sub2['BOND AMOUNT'].str.cat([df_sub2['BOND REMARKS'],
                                                                          [' Bond last updated']*df_sub2.shape[0],
                                                                          df_sub2['BOND LAST UPDATED']],
                                                                          sep=' ').str.cat(sep=' | ')
            
            # The reason this is not in bond_amount field
            # is because sometimes we can't match up charges 1-1 with the charge on the main page.
            # For example, sometimes several charges in main page turn into one charge in subpage.
            # Note main page already gives bond amount and whether they posted bond.
            if flag=='booking':
                supp_str = pd.Series(['Supplemental bond info for charge ']*df_sub2.shape[0]).str.cat(
                                                                 [df_sub2['CHARGE DESCRIPTION'],
                                                                 [': bond remarks ']*df_sub2.shape[0],
                                                                 df_sub2['BOND REMARKS'],
                                                                 [', bond last updated ']*df_sub2.shape[0],
                                                                 df_sub2['BOND LAST UPDATED']]).str.cat(sep=' | ')
                self.df.loc[ix,'other'] = self.df.loc[ix,'other'].str.cat([supp_str], sep=' | ')        

            # Set status for each charge like 'SENTENCED'. For this site, most statuses are blank.
            if flag=='roster': # nb see comment above for why we don't do this for flag==booking
                self.df.loc[ix, 'current_status'] = df_sub2['DISPOSITION'].str.replace('|',':').str.cat(sep=' | ')
                        
            # Set notes
            if self.df.loc[ix,'notes'].values != self.multi_booking_str:
                self.df.loc[ix,'notes'] = ''
            else:
                print(self.multi_booking_str)

            time.sleep(self.sleep_sec)
    
    
    
    def init_df(self, nrows):
        """ This will go in CSV file. """
        self.df = pd.DataFrame(np.zeros((nrows, 25)), columns=[
                  'county_name', # yes
                  'timestamp', # yes - time main page was scraped
                  'url', # yes - subpage urls (if couldn't connect, it's the main page url)
                  'inmate_id', # yes
                  'inmate_lastname', # yes
                  'inmate_firstname', # yes
                  'inmate_middlename', # yes
                  'inmate_sex', # yes
                  'inmate_race', # yes
                  'inmate_age', # yes - the age they turn on their birthdays in current year
                  'inmate_dob', # yes - only the year
                  'inmate_address', # yes - in subpages
                  'booking_timestamp', # yes
                  'release_timestamp', # yes - only for booking reports site, not for current roster site
                  'processing_numbers', # yes
                  'agency', # yes - in main page or subpages
                  'facility', # yes
                  'charges', # yes - in subpages
                  'severity', # yes - in subpages
                  'bond_amount', # yes - in main page or subpages
                  'current_status', # yes - in subpages
                  'court_dates',
                  'days_jailed',
                  'other', # yes for booking reports site - court jurisdiction & extra bond info
                  'notes']) # yes
        self.df[:] = '' # unfilled columns will be written to CSV as empty strings
        self.df['county_name'] = 'athens-clarke'
        self.df['facility'] = 'Clarke County Jail' # only one jail in this county, apparently
        self.df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')  # hardcoded EST because it's not critical to get the hour correct,
                                                                                 # timestamps are just for knowing roughly when we scraped.
 
    
    
    def format_bond_amount(self, dataframe):
        """ Formats a dollar string in dataframe column 
            If bond amount is '$0.00', '$' or '' there will be no dollar amount starting the bond_amount field,
            just ' ' then the bond remarks / bond last updated. """
        dataframe.loc[dataframe['BOND AMOUNT']=='$0.00','BOND AMOUNT'] = '' # Usually indicates no bond, not "released without bond"
        dataframe.loc[dataframe['BOND AMOUNT']=='$', 'BOND AMOUNT'] = '' # Sometimes this happens, not sure what it means
        dataframe['BOND AMOUNT'] = dataframe['BOND AMOUNT'].str.replace(',','') # Replace $1,000.00 with $1000.00



    def set_inmate_name(self, df_main):
        """ Set inmate last/first/middlename. Assumes format is "lastname, firstname zero or more middle names" """
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
        
        
        
    def set_inmate_sex(self, df_main):
        assert all(pd.notnull(df_main['SEX']))
        assert np.isin(df_main['SEX'].str.lower().unique(), np.array(['male','female'])).all(), "Invalid sex format"
        self.df['inmate_sex'] = df_main['SEX'].str.lower().str[0]
        
        
        
    def set_inmate_race(self, df_main):
        if any(pd.isnull(df_main['RACE'])):
            warn("At least one inmate's race was blank.")
            df_main['RACE'].fillna('', inplace=True)
        inmate_race = df_main['RACE'].str.lower() # don't have to convert 'asian' or 'white' because already listed that way
        inmate_race = inmate_race.str.replace('black/african american', 'black')\
                                 .str.replace('hispanic or latino', 'hispanic')\
                                 .str.replace('middle eastern decent', 'middle-eastern')\
                                 .str.replace('unknown', '') # leave race blank in this case. previous line: they had a "descent" typo
        assert np.isin(inmate_race.unique(), np.array(['asian','white','black','hispanic','middle-eastern',''])).all(),\
                     "One or more of these races not converted to standard format: " + str(inmate_race.unique())
        self.df['inmate_race'] = inmate_race
        
        
        
    def set_inmate_age(self, df_main):
        """ Set inmate age when we scraped the site.
            Because we only have birth year, age is whatever age they turn on their birthdays in the current year.
            That means it's impossible for 18 year olds (minimum booking age) to be incorrectly assigned age 17. """
        calc_age = lambda yyyy : str(datetime.now().year - int(yyyy))
        self.df['inmate_age'] = df_main['YEAR OF BIRTH'].apply(calc_age)
        
        
        
    def set_inmate_dob(self, df_main):
        """ Set inmate date of birth - only the year is available for Athens-Clarke county """
        assert all(pd.notnull(df_main['YEAR OF BIRTH']))
        assert all(df_main['YEAR OF BIRTH'].str.len()==4), 'Invalid year of birth format'
        self.df['inmate_dob'] = df_main['YEAR OF BIRTH']



    def set_booking_timestamp(self, df_main, booking_colname):
        """ Set booking timestamp from appropriate column.
            Hardcoding 'EST' because Athens-Clarke county is in Georgia USA
            See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
            Outputs 'YYYY-MM-DD HH:MM:SS EST', see https://docs.python.org/3/library/datetime.html#datetime.datetime.__str__ """            
        assert all(pd.notnull(df_main[booking_colname]))
        self.df['booking_timestamp'] = df_main[booking_colname].apply(self.convert_dt)



    def convert_dt(self, dt):
        return str(datetime.strptime(dt, "%m/%d/%Y %I:%M:%S %p")) + ' EST' # Format changes will likely be caught here



    def compress_inmate_rows(self, df_inmate):
        """ Used with pandas groupby & apply methods.
            df_inmate = self.df with only the rows for a single inmate.
            This compresses them into a single row and returns the row"""
    
        # Before compressing, check that rows are identical where they SHOULD be identical.
        # For example, the inmate's last name should be identical for each row in this group
        # (only checking rows obtained from main page data)
        errmsg = '>1 unique values in group column'
        assert df_inmate['inmate_lastname'].nunique()==1, errmsg
        assert df_inmate['inmate_firstname'].nunique()==1, errmsg
        assert df_inmate['inmate_middlename'].nunique()==1, errmsg
        assert df_inmate['inmate_sex'].nunique()==1, errmsg
        assert df_inmate['inmate_race'].nunique()==1, errmsg
        assert df_inmate['inmate_age'].nunique()==1, errmsg
        assert df_inmate['inmate_dob'].nunique()==1, errmsg

        # Copy it to avoid possible side effects
        # See https://pandas.pydata.org/pandas-docs/stable/generated/pandas.core.groupby.GroupBy.apply.html
        df_onerow = df_inmate.iloc[0,:].copy().to_frame().transpose()

        # Happens for "arrest from last 7 days" page if inmate was arrested, released, re-arrested in same week
        # In that case, pick the most recent booking
        if df_inmate['booking_timestamp'].nunique()>1: 
            df_onerow['booking_timestamp'] = max(pd.to_datetime(df_inmate['booking_timestamp'], format='%Y-%m-%d %H:%M:%S EST')).strftime('%Y-%m-%d %H:%M:%S EST')
            df_onerow['notes'] = self.multi_booking_str
            
        # Set the fields that are allowed to have different entries (one entry per charge), separated by ' | '
        df_onerow['release_timestamp'] = df_inmate['release_timestamp'].str.cat(sep=' | ')
        df_onerow['processing_numbers'] = df_inmate['processing_numbers'].str.cat(sep=' | ')
        if df_inmate['agency'].nunique()>1:
            warn("Multiple arresting agencies for inmate ID " + df_onerow.loc[df_onerow.index[0],'inmate_id'] + ". Inserting the agency that made the arrest for each charge")
            df_onerow['agency'] = df_inmate['agency'].str.cat(sep=' | ') # SHOULD be indented under if statement
        df_onerow['charges'] = df_inmate['charges'].str.cat(sep=' | ')
        df_onerow['severity'] = df_inmate['severity'].str.cat(sep=' | ')
        df_onerow['bond_amount'] = df_inmate['bond_amount'].str.cat(sep=' | ')
        df_onerow['other'] = df_inmate['other'].str.cat(sep=' | ')
        
        return df_onerow



    def dump(self, fid):
        """ dump to CSV """
        csv_fname = datetime.now().strftime('athens-clarke_' + fid + '_%Y_%m_%d_%H_%M_%S.csv')
        self.df.to_csv(self.csv_dir + '/' + csv_fname, index=False, line_terminator='\n') # matches default params for csv.writer
        print('Wrote ' + csv_fname + ' to ' + self.csv_dir)
    
    
    
    def get_page(self, url):
        """ Get html for a single page. If errors, retries loading page self.retries times.
            Returns html text (None if errors) 
            and error message (None if no errors)"""
        retries_left = self.retries
        while retries_left >= 0:
            try:
                response = requests.get(url, timeout=self.timeout, headers=self.headers)
                if response.status_code != requests.codes.ok:
                    raise requests.HTTPError('HTTP response code was {0}, should have been {1}'.format(response.status_code, requests.codes.ok))
                return response.text, None # no errors
            except Exception as e:
                errormsg = str(e)
                retries_left = retries_left - 1
        return None, errormsg # errors on the last attempt
    