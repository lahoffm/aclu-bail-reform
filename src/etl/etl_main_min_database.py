"""
    ETL to create SQLite database from webscraped county jail data in CSV files.

    Minimal database helps answer question
    "How long are misdemeanors in jail before getting released?"
    
    Code assumes CSVs are all in specified format INCLUDING CSV filename,
    doesn't do any checks. The checks should have been handled by webscrapers
    and unittest.
"""
import os
import glob
import pandas as pd
from datetime import datetime
import sqlite3
from init_min_database import init_min_database

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
# but only if release_timestamp is empty. Prevents Muscogee bug where we set
# release_timestamp back to '' if processing booking CSV after release CSV.
def update_rel_ts(bk_id_str, rel_ts):
    conn.execute('''
        UPDATE bookings SET release_timestamp = ?
        WHERE booking_id_string = ? AND release_timestamp = '';
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
    # When function runs for the next CSV file, it still detects
    # that booking exists in database but not in dataframe (inmate is still dropped
    # off roster) but release_timestamp was already set the last time, that's
    # why it checks for ''.
    for j in range(len(dropped_inmates)):
        conn.execute('''
            UPDATE bookings SET release_timestamp = ?
            WHERE booking_id_string = ? AND release_timestamp = '';
        ''',
        [rel_ts, dropped_inmates[j]])


# ETL configs
data_folder = '../../data' # all CSVs should be in here
counties =      ['athens-clarke',                'bibb', 'cobb', 'dekalb', 'fulton', 'glynn', 'muscogee'] # counties to add to database
start_strings = ['athens-clarke_booking-report', 'bibb', 'cobb', 'dekalb', 'fulton', 'glynn', 'muscogee'] # string the CSV filename should start with
db_dir = os.path.join(os.path.dirname(__file__), '../../data/databases')
sqlite_file = os.path.join(db_dir, 'min_booking_database.db')

# Create SQLite Minimum Database - this errors if db was already created,
# you should delete or rename the old file.
init_min_database(db_dir, sqlite_file)

# Connect to SQLite Minimum Database
conn = sqlite3.connect(sqlite_file)

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
    elif county == 'bibb':
        booking_id_fields = ['booking_timestamp', 'url'] # URL has both inmate ID and booking ID
    elif county == 'cobb':
        booking_id_fields = ['booking_timestamp', 'inmate_id']
    elif county == 'dekalb':
        booking_id_fields = ['booking_timestamp', 'inmate_id']
    elif county == 'fulton':
        booking_id_fields = ['booking_timestamp', 'inmate_id']
    elif county == 'glynn': 
        booking_id_fields = ['booking_timestamp', 'inmate_lastname',  # Glynn has no ID field, have to combine other info
                             'inmate_firstname', 'inmate_middlename', # WARNING: if 2 guys with same name & race arrested on same day,
                             'inmate_sex', 'inmate_race']             # it looks like 1 booking. Hopefully this happens rarely.
    elif county == 'muscogee':
        booking_id_fields = ['booking_timestamp', 'inmate_lastname',    # Muscogee has no ID field, have to combine other info
                             'inmate_firstname', 'inmate_middlename',   # WARNING: if 2 guys with same name & race & year of birth arrested on same day,
                             'inmate_sex', 'inmate_race', 'inmate_dob'] # it looks like 1 booking. Hopefully this happens rarely.   
    else:
        raise ValueError('County '  + county + ' does not have defined booking_id_fields')

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
        df = df.apply(lambda x: x.astype(str).str.lower()) # affects URLs and timestamp 'EST' to 'est' too! If change this also change 'est' where set below for Glynn
        
        # Get rid of felonies
        df = df[~df['severity'].str.contains('felony')] 

        # Make booking_timestamp 'YYYY-MM-DD 00:00:00 est' if booking_timestamp is 'YYYY-MM-DD'
        df['booking_timestamp'] = [(booking_timestamp if (':' in booking_timestamp or booking_timestamp == '') else booking_timestamp + ' 00:00:00 est') for booking_timestamp in df['booking_timestamp']]

        # Make release_timestamp 'YYYY-MM-DD 12:00:00 est' if release_timestamp is 'YYYY-MM-DD'
        df['release_timestamp'] = [(release_timestamp if (':' in release_timestamp or release_timestamp == '') else release_timestamp + ' 12:00:00 est') for release_timestamp in df['release_timestamp']]

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
        # update Glynn bookings with approximate release timestamp halfway between
        # current file and previous file because they dropped off roster during
        # that time interval.
        if county == 'glynn' and i > 0: 
            old_ts = fname_ts[i-1][1]
            rel_ts = old_ts + (ts - old_ts)/2
            rel_ts = rel_ts.strftime('%Y-%m-%d %H:%M:%S est')
            update_glynn_rel_ts(df, rel_ts)

conn.commit()

print('ETL completed successfully')
conn.close()
