#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 10:41:35 2017

@author: zander
"""

from scraper import scrape
from selenium import webdriver
import csv
import os
import re
from datetime import datetime

# This script runs each day. It starts by checking some log files that 
# initialize it. It then scrapes the Fulton County jail website, until some
# logic indicates it should stop scraping. It then saves a csv file containing 
# the data we scraped, and updates the log files for the next day.

# bring in info from log files

starting_record = 1721583

formatted_time = re.sub('[:\-\s]','_',str(datetime.now())[:-7])
csv_name_string = '../../../data/fulton'+'_'+formatted_time+'.csv'

dir_path = os.path.dirname(os.path.realpath(__file__))
chrome_path = os.path.join(dir_path,"chromedriver")
driver = webdriver.Chrome(chrome_path)

empty_counter = 0
unreleased = []
current_record = starting_record

fieldnames = ['county_name',
              'timestamp',
              'inmate_id',
              'inmate_lastname',
              'inmate_firstname',
              'inmate_middlename',
              'inmate_alias',
              'inmate_sex',
              'inmate_race',
              'inmate_address',
              'inmate_hair',
              'inmate_eyes',
              'inmate_weight',
              'inmate_height',
              'so_number',
              'booking_timestamp',
              'release_timestamp',
              'agency',
              'facility',
              'num_charges',
              'charges',
              'bond_amount',
              'notes'
        ]

with open(csv_name_string, 'a') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    
while True:
    cur_res = scrape(driver, current_record)
    if cur_res == []:
        empty_counter += 1
    else:
        empty_counter = 0
        
        par_res = {}
        par_res['notes'] = ''
        par_res['county_name'] = 'fulton'
        par_res['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')
        
        par_res['inmate_id'] = current_record
        par_res['inmate_lastname'] = cur_res[2][2].split(' ')[0].strip(',')
        par_res['inmate_firstname'] = cur_res[2][2].split(' ')[1].strip(',')
        try:
            par_res['inmate_middlename'] = cur_res[2][2].split(' ')[2].strip(',')
        except IndexError:
            par_res['inmate_middlename'] = None
        par_res['inmate_alias'] = cur_res[2][6]
        par_res['inmate_sex'] = cur_res[2][4].split('\xa0')[2][0]
        par_res['inmate_race'] = cur_res[2][4].split('\xa0')[0]
        # not totally sure if this is inmate address or address of the crime
        par_res['inmate_address'] = cur_res[2][14]
        par_res['inmate_hair'] = cur_res[2][8]
        par_res['inmate_eyes'] = cur_res[2][12]
        # weight in pounds
        par_res['inmate_weight'] = cur_res[2][4].split('\xa0')[6]
        inmate_feet = int(cur_res[2][4].split('\xa0')[4].split()[0][:-1])
        try:
            inmate_inches = int(cur_res[2][4].split('\xa0')[4].split()[1][:-1])
        except IndexError:
            inmate_inches = 0
        # height in inches
        par_res['inmate_height'] = inmate_feet * 12 + inmate_inches
        # not sure what SO number is
        par_res['so_number'] = cur_res[2][10]
        
        book_date = cur_res[1][1].split(':')[1].strip()
        try:
            par_res['booking_timestamp'] = datetime.strptime(book_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            par_res['notes'] = par_res['notes']+'no booking date recorded; '
        rel_date = cur_res[1][2].split(':')[1].strip()
        if rel_date == '':
            unreleased.append(current_record)
        else:
            par_res['release_timestamp'] = datetime.strptime(rel_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        
        par_res['agency'] = cur_res[0][1]
        par_res['facility'] = cur_res[1][0].split(':')[1]
        
        # seems bookings can have an arbitrary number of charges
        num_charges = len(cur_res) - 13
        par_res['num_charges'] = num_charges
        if num_charges > 0:
            par_res['charges'] = cur_res[13][1]
            # get bond just for first charge, in cents
            par_res['bond_amount'] =  ''.join(filter(str.isdigit, cur_res[13][4]))
        else:
            par_res['charges'] = None
            par_res['bond_amount'] = None
        
        with open(csv_name_string, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
            writer.writerow(par_res)
    
    if empty_counter > 20:
        break
    current_record += 1
        
        


#scraped_records = {}
#september = datetime.strptime('09/01/2017','%m/%d/%Y')
#def scrape_til_date(start_record, date):
#    current_record = start_record
#    while True:
#        scraped_records[current_record] = scrape(driver, current_record)
#        if current_record % 20 == 0:
#            if scraped_records[current_record] == []:
#                break
#            current_date_str = scraped_records[current_record][1][1].split(':')[1].strip()
#            current_date = datetime.strptime(current_date_str, '%m/%d/%Y')
#            if current_date > date:
#                return
#        current_record = current_record + 1
#        
#scrape_til_september(starting_record, september)


#driver.close()
