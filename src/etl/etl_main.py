"""
    ETL to get webscraped county jail data from CSV files into SQLite database.
    
    Code assumes CSVs are all in specified format INCLUDING CSV filename,
    doesn't do any checks. The checks should have been handled by webscrapers
    and unittest.

"""
import os
import glob
import pandas as pd
from datetime import datetime

# ETL configs
data_folder = '../../data' # all CSVs should be in here
counties = ['athens-clarke', 'bibb', 'dekalb', 'glynn', 'muscogee'] # counties to add to database

os.chdir(data_folder)
print('In folder ' + os.getcwd())
csv_files = glob.glob('*.csv')

for county in counties:
    print('Loading CSVs from ' + county + ' county')
    
    csv_county = [fname for fname in csv_files if fname.startswith(county)]
    
    # All filenames should end with "_YYYY-MM-DD_HH-MM-SS.csv" if specification was followed.
    # The two rfinds find the 2nd-last '_' in fname, which marks start of timestamp.
    # Then extract slice containing timestamp, 'YYYY-MM-DD_HH-MM-SS'
    timestamps = [fname[fname.rfind('_', 0, fname.rfind('_'))+1 : -4] for fname in csv_county]
    timestamps = [datetime.strptime(stamp, '%Y-%m-%d_%H-%M-%S') for stamp in timestamps]
    
    # Sort by timestamp so database always updated from earliest to most recent scrape
    fname_ts = list(zip(csv_county, timestamps))
    fname_ts = sorted(fname_ts, key=lambda x: x[1])
    
    for fname, ts in fname_ts:
        print('   Loading ' + fname + ' into database')
        
        if os.path.getsize(fname) == 0:
            print('        Empty file, skipping')
            continue

        df = pd.read_csv(fname, dtype=str)
        
        if df.shape[0] == 0:
            print('        Zero rows in file, skipping')
            continue

        # County-specific ETL code.
        # Differences between counties remain despite putting CSVs in same format,
        if county == 'athens-clarke':
            pass
        if county == 'bibb':
            pass
        if county == 'dekalb':
            pass
        if county == 'glynn':
            pass
        if county == 'muscogee':
            pass
    
print('ETL completed successfully')