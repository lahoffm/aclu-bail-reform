import csv
import re
import sys
from logger import *

# If there is a data format error, print error message with row number, field name, incorrect data, and correct format
def print_message(row, field, incorrect, correct):
  log_print_red("Row {} [{}]: '{}' should {}".format(row, field, incorrect, correct))

# If both charges and severity are not empty, check if count is equal
def check_charges_and_severity_count(row, charges, severity):
  if charges != '' and severity != '':
    if '|' in charges:
      try:
        assert len(charges.split('|')) == len(severity.split('|'))
      except AssertionError:
        log_print("Row " + row + " [charges & severity]: charges and severity should be the same count")

def validate_data(row, field, data, county):
  
  # To keep track of data format error status of file (True = has no error; False = has error)
  error_status = True

  # COUNTY_NAME (required)
  # Check if data matches county in file name
  if field == 'county_name':
    if data.lower() != county:
      print_message(row, field, data, "be '" + county + "'")

  # For all other fields besides county_name, ignore empty cells
  if data.strip() != '':

    # TIMESTAMP
    # Check if data is in 'YYYY-MM-DD hh:mm:ss EST' format
    if field == 'timestamp':
      if not re.match(r'^[1-2]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]\sEST$', data):
        print_message(row, field, data, 'be YYYY-MM-DD hh:mm:ss EST')   
        error_status = False

    # URL
    # Check if data starts with 'http://' or 'https://' followed by site address
    if field == 'url':
      if not re.match(r'^(http://|https://)\w+', data):
        print_message(row, field, data, 'be http://<address> or https://<address>')
        error_status = False

    # INMATE_LASTNAME, INMATE_FIRSTNAME, INMATE_MIDDLENAME
    # Check if data contains letters, periods, commas, spaces only (punctuation for titles (e.g. Jr.) and apostrophe names (e.g. O'Brien))
    if field in ('inmate_lastname', 'inmate_firstname', 'inmate_middlename'):
      if not re.match(r'^[A-z.,\-\' ]+$', data):
        print_message(row, field, data, 'contain letters, period, comma and apostrophe only')
        error_status = False

    # INMATE_SEX
    # Check if data is m or f
    if field == 'inmate_sex':
      if not re.match(r'^(m|f)$', data):
        print_message(row, field, data, 'be m or f')
        error_status = False

    # INMATE_RACE
    # Check if data is one of black, white, hispanic, asian, middle-easter, native-american, pacific-islander, multiracial, other
    if field == 'inmate_race':
      if not re.match(r'^(black|white|hispanic|asian|middle-eastern|native-american|pacific-islander|multiracial|other)$', data, re.IGNORECASE):
        print_message(row, field, data, 'black, white, hispanic, asian, middle-eastern, native-american, pacific-islander, multiracial, or other')
        error_status = False

    # INMATE_AGE
    # Check if data is an integer between 10 and 120
    if field == 'inmate_age':
      if (re.match(r'^\d+$', data)) and (10 <= int(data) <= 120):
        pass
      else:
        print_message(row, field, data, 'be an integer between 10 and 120')
        error_status = False

    # INMATE_DOB
    # Check if data is in YYYY-MM-DD or YYYY format
    if field == 'inmate_dob':
      if not re.match(r'(^[1-2]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])|^[1-2]\d{3})', data):
        print_message(row, field, data, 'be YYYY-MM-DD or YYYY')
        error_status = False

    # SEVERITY
    # Check if data is one of misdemeanor, felony, felony&misdemeanor
    if field == 'severity':
      if not re.match(r'^(misdemeanor|felony|felony&misdemeanor| )[ |]?', data, re.IGNORECASE):
        print_message(row, field, data, 'be misdemeanor, felony, or felony&misdemeanor')
        error_status = False

    # BOND_AMOUNT
    # Check if floats in data is preceded by $
    if field == 'bond_amount':
      if re.search(r'\d+\.\d{2}', data) and not re.search(r'\$\d+\.\d{2}', data):
        print_message(row, field, data, 'have $ before bond amount')
        error_status = False

    # DAYS_JAILES
    # Check if data is an integer
    if field == 'days_jailed':
      if not re.match(r'^[0-9]+$', data):
        print_message(row, field, data, 'be numbers only')
        error_status = False

    # COURT_DATES
    # Check if data is in YYYY-MM-DD format
    if field == 'court_dates':
      if not re.match(r'^[1-2]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])', data):
        print_message(row, field, data, 'be YYYY-MM-DD')
        error_status = False

    # BOOKING_TIMESTAMP, RELEASE_TIMESTAMP
    # Check if data is in 'YYYY-MM-DD hh:mm:ss EST' or 'YYYY-MM-DD' format (some counties don't provide time)
    if field in ('booking_timestamp', 'release_timestamp'):
      if not re.match(r'(^[1-2]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]\sEST|^[1-2]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]))$', data):
        print_message(row, field, data, 'be YYYY-MM-DD hh:mm:ss EST')   
        error_status = False

    # INMATE_ID, AGENCY, FACILITY
    # Check if data contains letters, numbers, spaces only
    if field in ('inmate_id', 'agency', 'facility'):
      if not re.match(r'^[A-z0-9 ]+$', data):
        print_message(row, field, data, 'contain letters and numbers only')
        error_status = False

    # INMATE_ADDRESS, PROCESSING_NUMBERS, CHARGES, CURRENT_STATUS
    # Check if data contains the following invalid characters: ~ + [ ] \ @ ^ { } % " * ` = ! ; ? $
    # (Will have to adjust character set according to tests)
    if field in ('inmate_address', 'processing_numbers', 'charges', 'current_status'):
      invalidCharacters = ['~', '+', '[', '\\', '@', '^', '{', '%', '"', '*', '`', '}', '=', ']', '!', ';', '?', '$']
      if any(char in data for char in invalidCharacters):
        print_message(row, field, data, 'not contain the following invalid characters: ~ + [ ] \ @ ^ { } % " * ` = ! ; ? $')
        error_status = False

  # Return error status of current file
  return error_status 


def validate_file(file):
    log_print('='*80)
    log_print_cyan('File: ' + file)

    # Reference for order of field names
    fieldnames_reference = ['county_name', 'timestamp', 'url', 'inmate_id', 'inmate_lastname', 'inmate_firstname', 'inmate_middlename', 'inmate_sex', 'inmate_race', 'inmate_age', 'inmate_dob', 'inmate_address', 'booking_timestamp', 'release_timestamp', 'processing_numbers', 'agency', 'facility', 'charges', 'severity', 'bond_amount', 'current_status', 'court_dates', 'days_jailed', 'other', 'notes']

    # To keep track of file validity
    passedValidation = True

    with open('./../data/' + file, 'r') as f:

      reader = csv.DictReader(f)
      
      header = reader.fieldnames

      # Check file header is in same order as fieldnames_reference (DOES NOT check for switched data; e.g. If charges and severity data are switched but header is in correct order, file will pass this test. Misplaced data will be caught in data validation process.)
      if header != fieldnames_reference:
        log_print('Field names do not match the required format. Order should be:\n{}'.format(('\n').join(fieldnames_reference)))
        # return
      # Get county of current file from file name
      county = file.split('_')[0]

      for i, row in enumerate(reader):

        # Add 2 to CSV row number to correspond to Excel row number
        row_num = str(i + 2)

        for field in row:

          # If passedValidation is True, update passedValidation until not True
          if passedValidation:
            passedValidation = validate_data(row_num, field, row[field], county)
          else:
            validate_data(row_num, field, row[field], county)

        # Check if charges and severity have the same count
        check_charges_and_severity_count(row_num, row['charges'], row['severity'])
    
    # If passedValidation is still True after validation check, print success message
    if passedValidation:
      log_print_green('Passed validation check.')