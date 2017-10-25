''' * Tests that CSV file made by a webscraper is in format specified by CONTRIBUTING.md.
    * Test results are appended to a logfile for current day.
    * Doesn't check for everything that could go wrong!
    * self.shortDescription() prints first line of method's docstring
        so logfile has more info of what was tested
    * To run on command line (looks for csv_fulename.csv in ../data folder)
        python csv_format_tester.py csv_filename.csv
'''
import unittest
import sys
import pandas as pd
from datetime import datetime

class TestCSV(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.csv = pd.read_csv(csv_fname)

    def test_headers(self):
        """ Column header names are in same order & identical to spec """
        msg = self.shortDescription()
        self.assertTrue(False, msg=msg)
        pass


    def test_num_columns(self):
        """ # columns in each row matches # column headers. Partial test that commas in fields were escaped correctly."""
        pass


    def test_keyboard_characters(self):
        """ Tests for characters that can't be typed on keyboard. Helps detect encoding problems. """
        pass


    # Subsequent methods test each data column.
    
    
    def test_county_name(self):
        """ """
        d = TestCSV.csv['county_name']
    
    
    def test_timestamp(self):
        """ """
        d = TestCSV.csv['timestamp']
        

    def test_url(self):
        """ """
        d = TestCSV.csv['url']
   
 
    def test_inmate_id(self):
        """ """
        d = TestCSV.csv['inmate_id']
 

    def test_inmate_lastname(self):
        """ """
        d = TestCSV.csv['inmate_lastname']
    
    
    def test_inmate_firstname(self):
        """ """
        d = TestCSV.csv['inmate_firstname']


    def test_inmate_middlename(self):
        """ """
        d = TestCSV.csv['inmate_middlename']
    
    
    def test_inmate_sex(self):
        """ """
        d = TestCSV.csv['inmate_sex']
    
    
    def test_inmate_race(self):
        """ """
        d = TestCSV.csv['inmate_race']
    
    
    def test_inmate_age(self):
        """ """
        d = TestCSV.csv['inmate_age']

    
    def test_inmate_dob(self):
        """ """
        d = TestCSV.csv['inmate_dob']
    
    
    def test_inmate_address(self):
        """ """
        d = TestCSV.csv['inmate_address']


    def test_booking_timestamp(self):
        """ """
        d = TestCSV.csv['booking_timestamp']
    
    
    def test_release_timestamp(self):
        """ """
        d = TestCSV.csv['release_timestamp']

    
    def test_processing_numbers(self):
        """ """
        d = TestCSV.csv['processing_numbers']
    
    
    def test_agency(self):
        """ """
        d = TestCSV.csv['agency']


    def test_facility(self):
        """ """
        d = TestCSV.csv['facility']
    
    
    def test_charges(self):
        """ """
        d = TestCSV.csv['charges']

    
    def test_severity(self):
        """ """
        d = TestCSV.csv['severity']
    
    
    def test_bond_amount(self):
        """ """
        d = TestCSV.csv['bond_amount']


    def test_current_status(self):
        """ """
        d = TestCSV.csv['current_status']
    
    
    def test_court_dates(self):
        """ """
        d = TestCSV.csv['court_dates']

    
    def test_days_jailed(self):
        """ """
        d = TestCSV.csv['days_jailed']
    
    
    def test_other(self):
        """ """
        d = TestCSV.csv['other']
    
    
    def test_notes(self):
        """ """
        d = TestCSV.csv['notes']
 

if __name__ == '__main__':
    csv_fname = '../data/' + sys.argv[-1] # Last command line arg must be CSV file to test, in ../data folder
    logfile = datetime.now().strftime('logs/csv_format_tester_log_%Y_%m_%d.log')
    log = open(logfile, "a") # put all tests for a given day in one logfile.
    log.write('\n' + '<'*100 + '\nStart test of CSV file ' + csv_fname + '\n')
    runner = unittest.TextTestRunner(log) # makes it output to logfile
    unittest.main(argv=sys.argv[0:-1], testRunner=runner)
    log.write('\nStop test of CSV file ' + csv_fname + '\n' + '>'*100 + '\n')
    log.close()