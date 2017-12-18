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

# Insert data into bookings database
def insert_booking(booking):
    conn.execute('''
        INSERT INTO bookings (booking_id_string, county_name, booking_timestamp, release_timestamp, known_misdemeanor)
        VALUES (?, ?, ?, ?, ?);
    ''',
    [
        booking['booking_id_string'],
        booking['county_name'],
        booking['booking_timestamp'],
        booking['release_timestamp'],
        int(booking['known_misdemeanor'])
    ])

# Update release_timestamp for non-Glynn bookings in database
def update_rel_ts(bk_id_str, rel_ts):
    conn.execute('''
        UPDATE bookings SET release_timestamp = ?
        WHERE booking_id_string = ?;
    ''',
    [rel_ts, bk_id_str])

# Update release_timestamp for Glynn bookings in database
def update_glynn_rel_ts(data, rel_ts):

    recent_roster = list()

    # Build list of bookings in current dataframe
    for i in range(data.shape[0]):
        row = data.iloc[i]
        if row['county_name'] == 'glynn':
            recent_roster.append(row['booking_id_string'])

    # Get list of bookings from database
    bookings_roster = list(map(lambda x:x[0], list(conn.execute('''
        SELECT booking_id_string
        FROM bookings
        WHERE county_name = 'glynn';
    '''))))

    # Get bookings that exist in database but not in dataframe
    dropped_inmates = list(set(bookings_roster) - set(recent_roster))

    # Update release_timestamp for dropped inmates in database
    for j in range(len(dropped_inmates)):
        conn.execute('''
            UPDATE bookings SET release_timestamp = ?
            WHERE booking_id_string = ? AND release_timestamp = '';
        ''',
        [rel_ts, dropped_inmates[j]])

# Connect to SQLite Minimum Database
conn = sqlite3.connect('../../data/databases/min_booking_database.db')

# ETL configs
data_folder = '../../data/athens_data' # all CSVs should be in here
counties =      ['athens-clarke',                'bibb', 'dekalb', 'glynn', 'muscogee', 'fulton'] # counties to add to database
start_strings = ['athens-clarke_booking-report', 'bibb', 'dekalb', 'glynn', 'muscogee_release', 'fulton'] # string the CSV filename should start with
sqlite_file = '../../data/databases/booking_database.db' # should already be initialized

os.chdir(data_folder)
print('In folder ' + os.getcwd())
csv_files = glob.glob('*.csv')

# For each county...
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
        temp_ts = fname_ts
    if county == 'muscogee':
        booking_id_fields = ['booking_timestamp', 'inmate_lastname',    # Muscogee has no ID field, have to combine other info
                             'inmate_firstname', 'inmate_middlename',   # WARNING: if 2 guys with same name & race & year of birth arrested on same day,
                             'inmate_sex', 'inmate_race', 'inmate_dob'] # it looks like 1 booking. Hopefully this happens rarely.   
    

    # For each file in county...
    for i in range(len(fname_ts)):
        
        fname = fname_ts[i][0]
        ts = fname_ts[i][1]
        

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
        
        # For Athens-Clarke county, if there are multiple release timestamps and all release timestamps are the same, release_timestamp is the first timestamp, else ''
        # Release timestamps should be the same if # of ' | ' is 1 less than # of same timestamp occurrences
        if county == 'athens-clarke':
            df['release_timestamp'] = [(release_timestamp.split(' | ')[0] if (release_timestamp.count(' | ') - release_timestamp.count(release_timestamp.split(' | ')[0]) == -1) else '') for release_timestamp in df['release_timestamp']]

        # If severity is 'misdemeanor' for every single charge, known_misdemeanor is 1, else 0
        # Number of 'misdemeanor' should == # of '|' - 1
        df['known_misdemeanor'] = [(1 if (severity.count('|') - severity.count('misdemeanor') == -1) else 0) for severity in df['severity']]
        
        # Concatenate to get unique ID string for each booking
        booking_id_string = df.loc[:,booking_id_fields]
        if len(booking_id_fields) > 1:
            booking_id_string = [booking_id_string[column] for column in booking_id_string.columns]
            booking_id_string = booking_id_string[0].str.cat(booking_id_string[1:], sep=' | ')
        df['booking_id_string'] = booking_id_string

        # For each row in file...
        for j in range(df.shape[0]):
            row = df.iloc[j]
            try:
                # Insert all new bookings to database
                insert_booking(row)
            except sqlite3.IntegrityError:
                # If booking already exists, update release_timestamp
                update_rel_ts(row['booking_id_string'], row['release_timestamp'])
                continue

        # If current county is Glynn and there are more than one Glynn files,
        # update Glynn bookings
        if county == 'glynn' and i > 0: 
            old_ts = fname_ts[i-1][1]
            rel_ts = old_ts + (ts - old_ts)/2
            rel_ts = rel_ts.strftime('%Y-%m-%d %H:%M:%S est')
            update_glynn_rel_ts(df, rel_ts)

conn.commit()

print('ETL completed successfully')
conn.close()
