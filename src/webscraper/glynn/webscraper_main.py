# Main webscraper script
# As of Oct 2017, glynncountysheriff.org had no robots.txt
import time
import requests
import tabula
import pandas as pd
import numpy as np
from datetime import datetime

t = time.time()

url = 'http://www.glynncountysheriff.org/data/Population.pdf'
r = requests.get(url, allow_redirects=True)
open('Population.pdf', 'wb').write(r.content)
    
# Read pdf into DataFrame
# Found these coordinates manually by running tabula.exe (in tabula subfolder)
# Drew boxes on the PDF, exported as a script file and copy-pasted coords into here.
# If PDF format ever changes, these coords have to be found again.
#
# area = [top (y), left (x), bottom (y), right (x)] of bounding box containing the table on each page.
# columns = x coordinates of column boundaries
# guess = False because we want it to grab all the data in the bounding box,
#         not guess which data to include.
print('Converting PDF to data frame...')
df_pdf = tabula.read_pdf("Population.pdf", pages='all', guess=False,
                     area=[79.695, 13.365, 576.675, 765.765], 
                     columns=[133.155, 208.395, 277.695, 327.195, 406.395, 765.765])

# Setup headers
df_pdf.columns = ['inmate_name', 'age_race_sex','booking_date','days_jailed','current_status','charges'] # easier to work with
df_pdf = df_pdf.iloc[1:,:] # drop 1st row, it just has more header text
df_pdf.reset_index(drop=True, inplace=True) # so indexes equal to self.df indexes

#csv_fname = 'out.csv'
#df_pdf.to_csv(csv_fname, index=True, line_terminator='\n') # matches default params for csv.writer

# Put inmate names on a single line.
# Takes advantage of pdf's format that age_race_sex always has 2 rows, so
# there's at least 2 data rows for each name. 
name_idx = pd.Series(df_pdf.index[df_pdf['booking_date'].notnull()]) # non-null booking dates indicate a name starts on this row
names = df_pdf['inmate_name'].fillna('')
df_pdf['inmate_name'] = np.nan
df_pdf.loc[name_idx,'inmate_name'] = names[name_idx].str.cat(names[name_idx+1], sep=' ').str.rstrip() # now, only name_idx rows are non-NaN

# Put age_race_sex on a single line
age_race_sex = df_pdf['age_race_sex']
df_pdf['age_race_sex'] = np.nan
df_pdf.loc[name_idx, 'age_race_sex'] = age_race_sex[name_idx].str.cat(age_race_sex[name_idx+1], sep=' ')

# Frequently, the inmate appearing at top of page is just continuation of the same inmate
# from last page. Get rid of continuances so each non-NaN inmate_name row indicates one person we can parse.
# Uniquely identify inmates by combining all available features.
inmate_id = df_pdf['inmate_name'].str.cat([df_pdf['age_race_sex'], df_pdf['booking_date'], df_pdf['days_jailed']], sep=' ')
all_id = inmate_id[name_idx]
idx_to_delete = all_id[all_id==all_id.shift(1)].index # if an inmate id matches the previous id, delete that row of duplicated information
df_pdf.loc[idx_to_delete,['inmate_name','age_race_sex','booking_date','days_jailed']] = np.nan # but don't delete current_status & charges, those aren't duplicated!

# TODO put charge degree and charges on a single line and extract charge severity

# Get rid of non-null rows since each inmate's info is now completely on one line.
df_pdf = df_pdf.loc[df_pdf['inmate_name'].notnull(),:].copy()
df_pdf.fillna('', inplace=True)
df_pdf.reset_index(drop=True, inplace=True) # so indexes equal to df indexes

# This will go in CSV
df = pd.DataFrame(np.zeros((df_pdf.shape[0], 25)), columns=[
          'county_name', # yes
          'timestamp', # yes
          'url', # yes
          'inmate_id',
          'inmate_lastname', # yes
          'inmate_firstname', # yes
          'inmate_middlename', # yes
          'inmate_sex', # yes
          'inmate_race', # yes
          'inmate_age', #  yes
          'inmate_dob', 
          'inmate_address',
          'booking_timestamp',  # yes - day only
          'release_timestamp',
          'processing_numbers',
          'agency',
          'facility', # yes
          'charges', # yes
          'severity', # yes - for some charges
          'bond_amount', 
          'current_status', # yes - for some charges
          'court_dates',
          'days_jailed',
          'other', 
          'notes'])

# Pro forma columns
df[:] = '' # unfilled columns will be written to CSV as empty strings
df['county_name'] = 'glynn'
df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')  # hardcoded EST because it's not critical to get the hour correct, timestamps are just for knowing roughly when we scraped.
df['url'] = url
df['facility'] = 'Glynn County Detention Center' # only one jail in this county, apparently


# Set inmate name
inmate_name = df_pdf['inmate_name'].str.split(', ', n=1, expand=True)
assert inmate_name.shape[1] == 2, 'Invalid name format'
df['inmate_lastname'] = inmate_name.iloc[:,0]
inmate_name = inmate_name.iloc[:,1]
inmate_name = inmate_name.str.split(' ', n=1, expand=True)
assert inmate_name.shape[1] == 2, 'Invalid name format'
inmate_name.fillna('', inplace=True)
df['inmate_firstname'] = inmate_name.iloc[:,0]
df['inmate_middlename'] = inmate_name.iloc[:,1]

# Set age, race, sex
age_race_sex = df_pdf['age_race_sex'].str.split(' ', expand=True)
df['inmate_age'] = age_race_sex.iloc[:,0]
inmate_race = age_race_sex.iloc[:,1]
assert np.isin(inmate_race.unique(), np.array(['B','W'])).all(),\
       "One or more of these races not converted to standard format: " + str(inmate_race.unique())
inmate_race = inmate_race.str.replace('B', 'black').str.replace('W', 'white')
df['inmate_race'] = inmate_race
inmate_sex = age_race_sex.iloc[:,3].str.lower()
assert np.isin(inmate_sex.unique(), np.array(['m','f'])).all(), 'Invalid sex format'
df['inmate_sex'] = inmate_sex

# Set booking date (time not provided)
# See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# Outputs 'YYYY-MM-DD', see https://docs.python.org/3/library/datetime.html#datetime.datetime.__str__ 
convert_date = lambda date: datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
df['booking_timestamp'] = df_pdf['booking_date'].apply(convert_date)

# Set days jailed
df['days_jailed'] = df_pdf['days_jailed']

# Set charges
df['charges'] = 'not set yet' #df_pdf['charges']

# Set severity
df['severity'] = 'not set yet'

# Set status of each charge
df['current_status'] = 'not set yet' #df_pdf['current_status']

# Dump to CSV
csv_dir = '../../../data' # where to write data
csv_fname = datetime.now().strftime('glynn_%Y_%m_%d_%H_%M_%S.csv')
df.to_csv(csv_dir + '/' + csv_fname, index=False, line_terminator='\n') # matches default params for csv.writer
print('Wrote ' + csv_fname + ' to ' + csv_dir)

elapsed = round(time.time() - t)
print('Seconds elapsed: ' + str(elapsed))
