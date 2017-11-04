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
from functools import reduce

# This script runs each day. It starts by checking some log files that 
# initialize it. It then scrapes the Fulton County jail website, until some
# logic indicates it should stop scraping. It then saves a csv file containing 
# the data we scraped, and updates the log files for the next day.

# bring in info from log files

current_record = int( open('last_record.txt','r').read() ) + 1

formatted_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_name_string = '../../../data/fulton'+'_'+formatted_time+'.csv'

dir_path = os.path.dirname(os.path.realpath(__file__))
chrome_path = os.path.join(dir_path,"chromedriver")
driver = webdriver.Chrome(chrome_path)

empty_counter = 0
unreleased = []

fieldnames = ['county_name',
              'timestamp',
              'url',
              'inmate_id',
              'inmate_lastname',
              'inmate_firstname',
              'inmate_middlename',
              'inmate_sex',
              'inmate_race',
              'inmate_age',
              'inmate_dob',
              'inmate_address',
              'booking_timestamp',
              'release_timestamp',
              'processing_numbers',
              'agency',
              'facility',
              'charges',
              'severity',
              'bond_amount',
              'current_status',
              'court_date',
              'days_jailed',
              'other',
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
        par_res['url'] = None
        par_res['inmate_age'] = None
        par_res['inmate_dob'] = None
        par_res['severity'] = None
        par_res['court_date'] = None
        par_res['days_jailed'] = None
        par_res['other'] = None
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
        par_res['inmate_sex'] = cur_res[2][4].split('\xa0')[2][0]
        par_res['inmate_race'] = cur_res[2][4].split('\xa0')[0]
        # not totally sure if this is inmate address or address of the crime
        par_res['inmate_address'] = cur_res[2][14]
        # not sure what SO number is
        par_res['processing_numbers'] = cur_res[2][10]
        
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
        if num_charges > 0:
            charge_list = [re.sub('|','',cur_res[13+i][1]) for i in range(num_charges)]
            par_res['charges'] = reduce((lambda x,y: x + ' | ' + y), charge_list)
            
            bond_list = [re.sub('\D','',cur_res[13+i][4])[:-2] for i in range(num_charges)]
            for i in range(len(bond_list)):
                if bond_list[i] != '':
                    bond_list[i] = '$' + bond_list[i]
            par_res['bond_amount'] = reduce((lambda x,y: x + ' | ' + y), bond_list)
            
            disp_list = [re.sub('|','',cur_res[13+i][6]) for i in range(num_charges)]
            par_res['current_status'] = reduce((lambda x,y: x + ' | ' + y), disp_list)
            
        else:
            par_res['charges'] = None
            par_res['bond_amount'] = None
            par_res['current_status'] = None
        
        with open(csv_name_string, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
            writer.writerow(par_res)
    
    if empty_counter >= 20:
        break
    current_record += 1
        
last_record_scraped = current_record - 20

with open('last_record.txt', 'w') as f:
    f.write(str(last_record_scraped))


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
