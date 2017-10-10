# Main webscraper script
import time
import requests
import tabula
import pandas as pd
import numpy as np


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
df = tabula.read_pdf("Population.pdf", pages='all', guess=False,
                     area=[79.695, 13.365, 576.675, 765.765], 
                     columns=[133.155, 208.395, 277.695, 327.195, 406.395, 765.765])
csv_fname = 'out.csv'
df.to_csv(csv_fname, index=False, line_terminator='\n') # matches default params for csv.writer

# convert PDF into CSV
print('Wrote to csv')

elapsed = round(time.time() - t)
print('Seconds elapsed: ' + str(elapsed) + ', minutes elapsed: ' + str(elapsed/60))
