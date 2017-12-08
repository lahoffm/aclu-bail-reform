# Convenience script to make multiple CSV files going back 30 days in the past

import os

for i in range(1,31):    
    os.system('python cobb_scraper.py ' + str(i))
