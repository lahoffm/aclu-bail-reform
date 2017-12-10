import os
import sys
from validator import validate_file
from logger import *
from datetime import datetime

log_print('\nDate: ' + datetime.now().strftime('%Y_%m_%d') + '\nValidating files...\n')

directory = os.path.relpath('./../data');
for root, dirs, files in os.walk(directory):
  for file in files:
    if file.endswith('.csv'):
      validate_file(directory, file);

log_print('\n' + '-'*80 + '\nValidation check done.\n')