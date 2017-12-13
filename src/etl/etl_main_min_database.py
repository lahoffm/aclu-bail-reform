"""
    ETL to get webscraped county jail data from CSV files into SQLite database.

    Appends to minimal database to help answer question
    "How long are misdemeanors in jail before getting released?"
    
    Code assumes CSVs are all in specified format INCLUDING CSV filename,
    doesn't do any checks. The checks should have been handled by webscrapers
    and unittest.

    Code assumes database file was already initialized.

"""
import os
import glob
import pandas as pd
from datetime import datetime
import sqlite3

conn = sqlite3.connect('../../data/databases/min_booking_database.db')

# ETL configs
data_folder = '../../data' # all CSVs should be in here
counties =      ['athens-clarke',                'bibb', 'dekalb', 'glynn', 'muscogee', 'fulton'] # counties to add to database
start_strings = ['athens-clarke_booking-report', 'bibb', 'dekalb', 'glynn', 'muscogee_release', 'fulton'] # string the CSV filename should start with
sqlite_file = '../../data/databases/booking_database.db' # should already be initialized

os.chdir(data_folder)
print('In folder ' + os.getcwd())
csv_files = glob.glob('*.csv')

for county, start_string in zip(counties, start_strings):
    print('Loading CSVs from ' + county + ' county')
    
    csv_county = [fname for fname in csv_files if fname.startswith(start_string)]

    # All filenames should end with "_YYYY-MM-DD_HH-MM-SS.csv" if specification was followed.
    # The two rfinds find the 2nd-last '_' in fname, which marks start of timestamp.
    # Then extract slice containing timestamp, 'YYYY-MM-DD_HH-MM-SS'
    timestamps = [fname[fname.rfind('_', 0, fname.rfind('_'))+1 : -4] for fname in csv_county]
    timestamps = [datetime.strptime(stamp, '%Y-%m-%d_%H-%M-%S') for stamp in timestamps]
    
    # Sort by timestamp so database always updated from earliest to most recent scrape
    fname_ts = list(zip(csv_county, timestamps))
    fname_ts = sorted(fname_ts, key=lambda x: x[1])
    
    # Which fields form unique identifiers for each booking
    # Differences between counties remain despite putting CSVs in same format
    if county == 'athens-clarke':
        booking_id_fields = ['booking_timestamp', 'inmate_id'] 
    if county == 'bibb':
        booking_id_fields = ['booking_timestamp', 'url'] # URL has both inmate ID and booking ID
    if county == 'dekalb':
         booking_id_fields = ['booking_timestamp', 'inmate_id']
    if county == 'glynn': 
        booking_id_fields = ['booking_timestamp', 'inmate_lastname',  # Glynn has no ID field, have to combine other info
                             'inmate_firstname', 'inmate_middlename', # WARNING: if 2 guys with same name & race arrested on same day,
                             'inmate_sex', 'inmate_race']             # it looks like 1 booking. Hopefully this happens rarely.
    if county == 'muscogee':
        booking_id_fields = ['booking_timestamp', 'inmate_lastname',    # Muscogee has no ID field, have to combine other info
                             'inmate_firstname', 'inmate_middlename',   # WARNING: if 2 guys with same name & race & year of birth arrested on same day,
                             'inmate_sex', 'inmate_race', 'inmate_dob'] # it looks like 1 booking. Hopefully this happens rarely.   
    
    for fname, ts in fname_ts:
        print('   Loading ' + fname + ' into database')
        
        # Get dataframe
        if os.path.getsize(fname) == 0:
            print('        Empty file, skipping')
            continue
        df = pd.read_csv(fname, dtype=str)
        if df.shape[0] == 0:
            print('        Zero rows in file, skipping')
            continue
        df.fillna('', inplace=True)
        df = df.apply(lambda x: x.astype(str).str.lower()) # affects URLs and timestamp 'EST' to 'est' too!
        
        # Get rid of felonies
        df = df[~df['severity'].str.contains('felony')] 
        
        # If severity is 'misdemeanor' for every single charge, known_misdemeanor is 1, else 0
        # number of 'misdemeanor' should == # of '|' - 1
        df['known_misdemeanor'] = [(1 if (severity.count('|') - severity.count('misdemeanor') == -1) else 0) for severity in df['severity']]
        
        # Concatenate to get unique ID string for each booking
        booking_id_string = df.loc[:,booking_id_fields]
        if len(booking_id_fields) > 1:
            booking_id_string = [booking_id_string[column] for column in booking_id_string.columns]
            booking_id_string = booking_id_string[0].str.cat(booking_id_string[1:], sep=' | ')
        df['booking_id_string'] = booking_id_string
    
        insert_statement = '''
                INSERT INTO bookings (booking_id_string, county_name, booking_timestamp, release_timestamp, on_roster, known_misdemeanor) 
                VALUES (?, ?, ?, ?, ?, ?)
            '''

        for i in range(df.shape[0]):
            row = df.iloc[i]
            known_misdemeanor = df['known_misdemeanor'][i]
            on_roster = 0

            try:
                conn.execute(insert_statement, (row['booking_id_string'], row['county_name'], row['booking_timestamp'], row['release_timestamp'], on_roster, known_misdemeanor))
            except sqlite3.IntegrityError:
                print("This was added before")
                continue

    conn.commit()
print('ETL completed successfully')
conn.close()
