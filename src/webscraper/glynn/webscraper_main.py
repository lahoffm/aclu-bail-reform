# Main webscraper script
# As of Oct 2017, glynncountysheriff.org had no robots.txt
import requests
import tabula
import pandas as pd
import numpy as np
from datetime import datetime
from warnings import warn

# Get PDF, write to data dir for diagnosis if something goes wrong.
print('Running Glynn county webscraper')
url = 'http://www.glynncountysheriff.org/data/Population.pdf'
response = requests.get(url, allow_redirects=True)
timestamp = datetime.now()
data_dir = '../../../data' # where to write data
pdf_fname = timestamp.strftime('glynn_%Y_%m_%d_%H_%M_%S.pdf')
f = open(data_dir + '/' + pdf_fname, 'wb')
f.write(response.content)
f.close()
print('Wrote ' + pdf_fname + ' to ' + data_dir)

# Read pdf into DataFrame
# Found these coordinates manually by running tabula.exe (in tabula subfolder)
# Drew boxes on the PDF, exported as a script file and copy-pasted coords into here.
# If PDF format ever changes, these coords have to be found again.
#
# area = [top (y), left (x), bottom (y), right (x)] of bounding box containing the table on each page.
# columns = x coordinates of column boundaries
# guess = False because we want it to grab all the data in the bounding box,
#         not guess which data to include.
print('Loading PDF...')
df_pdf = tabula.read_pdf(data_dir + '/' + pdf_fname, pages='all', guess=False,
                          pandas_options={'dtype':{"Inmate's Name" : str, # parse all columns as strings
                                                   'Age' :           str,
                                                   'Booking' :       str,
                                                   'Days' :          str,
                                                   'Charge' :        str,
                                                   'Charges' :       str}},
                     area=[79.695, 13.365, 576.675, 765.765],
                     columns=[133.155, 208.395, 277.695, 327.195, 406.395, 765.765])
assert all(df_pdf.columns==["Inmate's Name", 'Age', 'Booking', 'Days', 'Charge', 'Charges']), 'Column names have changed'             
assert df_pdf.iloc[0,:].str.cat()=='Race / GenderDateJailedDegree', 'Column names have changed'

# Load charges into a Series.
# Although df_pdf has the same charges text, there's no way to tell which charges are one-liners or two-liners.
# That's because two-line charges are put into two separate cells in the dataframe.
# Unfortunately, this means 2-line charges look identical to one-line charges.
# Fortunately, by selecting just the Charges column and using 'lattice' mode, we can load each charge into a single cell.
# Two-line charges are separated by '\r' - later code will make use of this fact.
# We can't use lattice mode to load df_pdf because the lattice structure isn't consistent across columns.
# NB lattice is faintly visible as thin white lines when you open the PDF using tabula.exe
charges = tabula.read_pdf(data_dir + '/' + pdf_fname, pages='all', guess=False, lattice=True,
                     pandas_options={'header': None, # for Glynn's PDF, header on 1st page isn't part of the lattice
                                     'names': ['blank', 'charges'], # blank column is all NaN
                                     'dtype':{'charges': str}},
                     area=[79.695, 406.395, 576.675, 765.765], # top (y), left (x), bottom (y), right (x) of bounding box containing charges on each page
                     columns=[406.395, 765.765]) # make column boundary explicit, prevents splitting up charges into 2 columns
charges = charges['charges']

# Initial dataframe formatting
print('Converting PDF to CSV format...')
df_pdf.columns = ['inmate_name', 'age_race_sex','booking_date','days_jailed','current_status','charges'] # easier to work with
total_inmates = df_pdf.iloc[-1,0]
assert total_inmates.startswith('Total Inmates: '), 'PDF does not end with a count of total inmates'
total_inmates = int(total_inmates[15:])
df_pdf = df_pdf.iloc[1:-1,:] # drop 1st row, it just has more header text. drop last row, it just lists total inmates
df_pdf.reset_index(drop=True, inplace=True) # so indexes equal to self.df indexes and a loop below can index by 0, 1, ...

# For debugging
#df_pdf.to_csv('debug.csv', index=True, line_terminator='\n')

# Checks that # of charges loaded is consistent.
# First, we get total number of lines in df_pdf containing the descriptive text.
# Second, we know df_pdf splits 2-line charges across two cells so we can't just compare it to charges.shape[0].
# Therefore we add the number of '\r' in charges since this indicates 2-line charges.
# This also makes sure there's no 3-line charges - we would miss adding the second '\r' and assertion would fail
assert sum(df_pdf['charges'].notnull()) == (charges.shape[0] + sum(charges.str.contains('\r'))), '# charges when loading entire pdf != # charges when loading just the "Charges" column'

# Put inmate names on a single line.
# Takes advantage of pdf's format that age_race_sex always has 2 rows, so
# there's at least 2 data rows for each name. 
# If inmate's name is on 3 rows (should be very rare) we don't care, we'll still get most of the name
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
# If inmate is on >2 consecutive pages, it still works correctly!
inmate_id = df_pdf['inmate_name'].str.cat([df_pdf['age_race_sex'], df_pdf['booking_date'], df_pdf['days_jailed']], sep=' ')
all_id = inmate_id[name_idx]
idx_to_delete = all_id[all_id==all_id.shift(1)].index # if an inmate id matches the previous id, delete that row of duplicated information
df_pdf.loc[idx_to_delete,['inmate_name','age_race_sex','booking_date','days_jailed']] = np.nan # but don't delete current_status & charges, those aren't duplicated!
num_inmates = sum(df_pdf['inmate_name'].notnull())
if num_inmates != total_inmates: # Expecting this to be rare.
    # Probably happens if loading PDF when they are in the middle of updating their database.
    # Will hardly affect data analysis if 1/500 inmates in 1/10 downloaded PDFs has this problem, best to just proceed.
    warn("After preprocessing, # inmates in dataframe ("  + str(num_inmates) + ') != total inmate count at bottom of PDF (' +
         str(total_inmates) + "). This probably happened because one or more booking dates weren't filled in." +
         ' As a result, at least one inmate will mistakenly be assigned the charges that should go to another inmate.')

# Put each charge on a single line - comments earlier explain why we have to do it this way.
j = 0
charges_oneline = charges.str.replace('\r', ' ')
for i in range(len(charges)):
    if '\r' in charges[i]: # two-line charge
        firstline = charges[i][0:charges[i].find('\r')]
    else: # one-line charge
        firstline = charges[i]
    while True: # go to next line matching current charge
        if df_pdf.loc[j,'charges']==firstline:
            break
        j += 1
    if '\r' in charges[i]: # must concatenate for two-line charge
        df_pdf.loc[j,'charges'] = df_pdf.loc[j,'charges'] + ' ' + df_pdf.loc[j+1,'charges']
        df_pdf.loc[j+1,'charges'] = ''
    assert charges_oneline[i] == df_pdf.loc[j,'charges'], 'When 2-line charge was concatenated to one line, it did not match the expected one-line charge'
    j += 1

# Helper function to put each current status on one line
# Makes two-line status to a one-line status
def combine_twoline_status(str1, str2, oneOption=True): # 
    idx = df_pdf.index[df_pdf['current_status'] == str1]
    idx2 = df_pdf.index[df_pdf['current_status'] == str2]
    assert all(df_pdf.loc[idx2-1, 'current_status'] == str1), "Row before '" + str2 + "' should be '" + str1 + "'"
    if oneOption: # only check where str1 should always be followed by str2
        assert all(df_pdf.loc[idx+1, 'current_status'] == str2), "Row after '" + str1 + "' should be '" + str2 + "'"
    df_pdf.loc[idx2-1, 'current_status'] = str1 + ' ' + str2
    df_pdf.loc[idx2, 'current_status'] = ''

# Put each current status on a single line. Most already are, but some are on 2 or 3 lines.
df_pdf['current_status'].fillna('', inplace=True)
assert np.isin(df_pdf['current_status'].unique(), np.array(['',
                                                            'Dismissed',
                                                            'Sentenced',
                                                            'Nolle Prosequi',
                                                            'Court Release',
                                                            'Time Served',
                                                            'Municipal Court', # part of two-liner
                                                            'Release', # part of two-liner
                                                            'No Warrant', # part of two-liner
                                                            'Received', # part of two-liner
                                                            'Erroneous Release',
                                                            'Transferred',
                                                            'Posted Bond',
                                                            'Probation', # part of two-liner
                                                            'Revocation', # part of two-liner
                                                            'Probation Expired',
                                                            'Charges Amended', # part of two or three-liner
                                                            'at Preliminary', # part of three-liner
                                                            'Hearing', # part of three-liner
                                                            'at Superior Court', # part of two-liner
                                                            'Parole Release'])).all(), "Invalid format for charges' current status."
combine_twoline_status('Municipal Court', 'Release')
combine_twoline_status('No Warrant', 'Received')
combine_twoline_status('Probation', 'Revocation')
combine_twoline_status('at Preliminary', 'Hearing') # first combine line 2+3 of a three-line status
combine_twoline_status('Charges Amended', 'at Preliminary Hearing', oneOption=False) # can be followed either by 'at Preliminary Hearing' or 'at Superior Court'
combine_twoline_status('Charges Amended', 'at Superior Court') # After the last statement, this should be only option left

# Extract charge severity (not all charges list this)
df_pdf['severity'] = ''
felony_mask = df_pdf['charges'].str.lower().str.contains('felony', na=False)
misdemeanor_mask = df_pdf['charges'].str.lower().str.contains('misdemeanor', na=False)
df_pdf.loc[felony_mask,'severity'] = 'felony'
df_pdf.loc[misdemeanor_mask,'severity'] = 'misdemeanor' 

# Helper function to compress each inmate's data into one row.
# Combines the inmate's charges, current_status, and severity into one line, separated by ' | '
# The inmate's remaining data columns are already on the first row because of processing above.
# Return dataframe with one row containing all the inmate's data
def compress_inmate_rows(df_inmate):
    # Copy it to avoid possible side effects
    # See https://pandas.pydata.org/pandas-docs/stable/generated/pandas.core.groupby.GroupBy.apply.html
    df_onerow = df_inmate.iloc[0,:].copy().to_frame().transpose()
    keep_rows = df_inmate['charges'] != '' # Don't keep empty charges rows.
                                           # Earlier code put current_status and severity on same row as the corresponding charge
    df_onerow['current_status'] = df_inmate.loc[keep_rows, 'current_status'].str.cat(sep=' | ')
    df_onerow['charges'] = df_inmate.loc[keep_rows, 'charges'].str.cat(sep=' | ')
    df_onerow['severity'] = df_inmate.loc[keep_rows, 'severity'].str.cat(sep=' | ')
    return df_onerow

# Compress each inmate's data into one row via pandas split/apply/combine.
# Set a unique ID for each of the inmate's rows, group by inmate, compress to one row.
# Each group has all the data for one inmate.
name_idx = df_pdf.index[df_pdf['inmate_name'].notnull()]
assert name_idx[0]==0, "First inmate's name must be on first row"
df_pdf['inmate_id'] = name_idx[-1] # np.int64. After loop finishes, inmate_id[name_idx[-1]:-1] = id of the last inmate
for i in range(len(name_idx)-1):
    df_pdf.loc[name_idx[i] : (name_idx[i+1]-1), 'inmate_id'] = name_idx[i]
df_pdf.fillna('', inplace=True) # so we save empty columns as '' and compress_inmate_rows selects the right rows
inmate_groups = df_pdf.groupby('inmate_id', sort=False, as_index=False)
df_pdf = inmate_groups.apply(compress_inmate_rows)
df_pdf.reset_index(drop=True, inplace=True) # so indexes equal to df indexes
df_pdf.drop('inmate_id', axis=1, inplace=True)

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
          'days_jailed', # yes
          'other', 
          'notes']) # yes - says if the charge is not in the dictionary listing one-line or two-line charges

# Pro forma columns
df[:] = '' # unfilled columns will be written to CSV as empty strings
df['county_name'] = 'glynn'
df['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S EST')  # hardcoded EST because it's not critical to get the hour correct, timestamps are just for knowing roughly when we scraped.
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
assert age_race_sex.shape[1] == 4, 'Invalid age/race/sex format'
assert all(age_race_sex.iloc[:,2]=='/'), 'Race and sex should be separated by " / "'
try:
    pd.to_numeric(age_race_sex.iloc[:,0]) # checks that age is a number (but we still save it as a string)
except ValueError as e:
    raise ValueError('Unable to convert inmate age to numeric')
df['inmate_age'] = age_race_sex.iloc[:,0]
inmate_race = age_race_sex.iloc[:,1]
assert np.isin(inmate_race.unique(), np.array(['B','W'])).all(),\
       "One or more of these races not converted to standard format: " + str(inmate_race.unique())
df['inmate_race'] = inmate_race.str.replace('B', 'black').str.replace('W', 'white')
inmate_sex = age_race_sex.iloc[:,3].str.lower()
assert np.isin(inmate_sex.unique(), np.array(['m','f'])).all(), 'Invalid sex format'
df['inmate_sex'] = inmate_sex

# Set booking date (time not provided)
# See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# Outputs 'YYYY-MM-DD', see https://docs.python.org/3/library/datetime.html#datetime.datetime.__str__ 
convert_date = lambda date: datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
df['booking_timestamp'] = df_pdf['booking_date'].apply(convert_date)

# Set days jailed
try:
    pd.to_numeric(df_pdf['days_jailed']) # checks that days_jailed is a number (but we still save it as a string)
except ValueError as e:
    raise ValueError('Unable to convert days_jailed to numeric')
df['days_jailed'] = df_pdf['days_jailed']

# Set charges
df['charges'] = df_pdf['charges']

# Set severity
df['severity'] = df_pdf['severity']

# Set status of each charge
df['current_status'] = df_pdf['current_status']

# Dump to CSV
csv_fname = timestamp.strftime('glynn_%Y_%m_%d_%H_%M_%S.csv')
df.to_csv(data_dir + '/' + csv_fname, index=False, line_terminator='\n') # matches default params for csv.writer
print('Wrote ' + csv_fname + ' to ' + data_dir)
