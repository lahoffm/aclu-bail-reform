import os
import sys
from validator import validate_file

directory = os.path.relpath('./../data');
for root, dirs, files in os.walk(directory):
  for file in files:
    if file.endswith('.csv'):
      validate_file(file);

print('=======================================================================================')
print('Validation check done.')