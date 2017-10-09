import requests
import json
import req_data
import csv
from nameparser import HumanName
import datetime

base_url = 'https://ody.dekalbcountyga.gov'

search_url = base_url + '/app/JailSearchService/search'

req_post = requests.post(search_url, json=req_data.search_payload, headers=req_data.search_headers)

data = req_post.json()

inmate_data = list(data['searchResult']['hits'])

# print(json.dumps(inmate_list, indent=2))

inmate_list = []

for inmate in inmate_data:
  name = HumanName(inmate['defendantName'])

  view_url = base_url + inmate['webIntents'][0]['uri']

  inmate_dict = {
    'county_name': 'dekalb',
    'timestamp': None,
    'url': view_url,
    'inmate_id': inmate['defendantSONum'],
    'inmate_lastname': name.last,
    'inmate_firstname': name.first,
    'inmate_middlename': name.middle,
    'inmate_sex': None,
    'inmate_race': None,
    'inmate_age': None,
    'inmate_dob': inmate['defendantDOB'],
    'inmate_address': None,
    'booking_timestamp': None,
    'release_timestamp': None,
    'processing_numbers': None,
    'agency': inmate['arrests'][0]['arrestingAgency'],
    'facility': inmate['facility'],
    'charges': None,
    'severity': None,
    'bond_amount': None,
    'current_status': None,
    'court_dates': None,
    'days_jailed': None,
    'other': None,
    'notes': None,
    'inmate_type': inmate['type'],
    'booking_date': inmate['bookingDate'],
    'booking_number': inmate['bookingNumber'],
    'arrest_id': inmate['arrests'][0]['arrestID'],
    'arresting_agency': inmate['arrests'][0]['arrestingAgency'],
    'charge_description': inmate['charges'][0]['chargeDescription'],
    'jail_id': inmate['jailID'],
    'release_date': inmate['releaseDate'],
    'charge_count': inmate['chargeCount'],
    'booking_time': inmate['bookingTime'],
    'release_time': inmate['releaseTime'],
    'so_num': inmate['defendantSONum']
  }

  inmate_list.append(inmate_dict)

with open('dekalb.csv', 'w') as new_file:

  fieldnames = list(inmate_dict.keys())

  csv_writer = csv.writer(new_file, delimiter=',')

  csv_writer.writerow(fieldnames)

  csv_writer.writerow(dict(inmate_dict))
  

# message = '''
# SO#: {so_num}
# First Name: {inmate_firstname}
# Last Name: {inmate_lastname}
# Middle Name: {inmate_middlename}
# Sex: 
# Race: 
# Age: 
# Address: 
# Bond Amount: 
# DOB: {inmate_dob}
# Facility: {facility}
# Jail ID: {jail_id}
# Arrest ID: {arrest_id}
# Booking Number: {booking_number}
# Booking Date: {booking_date}
# Booking Time: {booking_time}
# Type: {inmate_type}
# Arresting Agency: {arresting_agency}
# Charge Count: {charge_count}
# Charge Description: {charge_description}
# Release Date: {release_date}
# Release Time: {release_time}
# URL: {url}
# '''.format(**inmate_dict)

# print(message)

# print(json.dumps(inmate, indent=2))


# JAIL SEARCH========================================
# url                 | {inmate_uri}
# inmate_id           | //refer to other IDs
# inmate_so           | {so_num}
# arrest_id           | {arrest_id}
# inmate_lastname     | {inmate_name} parsed
# inmate_firstname    | {inmate_name} parsed
# inmate_middlename   | {inmate_name} parsed
# inmate_dob          | {inmate_dob}
# booking_timestamp   | {booking_date} + {booking_time}
# release_timestamp   | {release_date} + {release_time}
# processing_numbers  | //refer to other IDs
# agency              | {arresting_agency}
# charges             | {charge_description} 
# charge_count        | {charge_count}




# JAIL VIEW==========================================
# inmate_sex          |
# inmate_race         |
# inmate_age          |
# inmate_address      |
# bond_amount         |
# total_due           |


# OTHER===============================================
# county_name         | dekalb
# timestamp           | 
# days_jailed         | {current_timestamp} - {booking_timestamp}
# current_status      |
# court_dates         |
# other               |
# notes               |