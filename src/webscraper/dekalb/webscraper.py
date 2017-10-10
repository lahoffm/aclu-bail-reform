import requests
import json
import req_data
import csv
from nameparser import HumanName
import datetime

def get_charges(charges):
  charges_list = []
  for charge in charges:
    charges_list.append(charge['ChargeDescription'])
  return charges_list

req_post = requests.post('https://ody.dekalbcountyga.gov/app/JailSearchService/search', json=req_data.search_payload, headers=req_data.search_headers)
search_results = req_post.json()
inmate_data = list(search_results['searchResult']['hits'])
print(json.dumps(inmate_data, indent=2))

inmate_list = []

for inmate in inmate_data:
  name = HumanName(inmate['defendantName'])
  jail_id = str(inmate['jailID'])
  view_url = 'https://ody.dekalbcountyga.gov/app/ViewJailing/#/jailing/' + jail_id
  req_get = requests.get('https://ody.dekalbcountyga.gov/app/ViewJailingService//Jailings(' + jail_id + ')')
  jailing_data = req_get.json()

  print(json.dumps(jailing_data, indent=2))



  inmate_dict = {
    'county_name': 'dekalb',
    'timestamp': None,
    'url': view_url,
    'inmate_id': jail_id,
    'inmate_lastname': name.last,
    'inmate_firstname': name.first,
    'inmate_middlename': name.middle,
    'inmate_sex': jailing_data['DefendantGender'],
    'inmate_race': jailing_data['DefendantRace'],
    'inmate_age': None,
    'inmate_dob': inmate['defendantDOB'],
    'inmate_address': ', '.join(jailing_data['DefendantAddress']),
    'booking_timestamp': inmate['bookingDate'],
    'release_timestamp': inmate['releaseDate'],
    'processing_numbers': ' | '.join([
        'so#=' + str(inmate['defendantSONum']),
        'booking#=' + str(inmate['bookingNumber']),
        'jailID=' + str(inmate['jailID']),
        'arrestID=' + str(inmate['arrests'][0]['arrestID'])
      ]),
    'agency': inmate['arrests'][0]['arrestingAgency'],
    'facility': jailing_data['Facility'],
    'charges': ' | '.join(get_charges(jailing_data['Charges'])),
    'severity': None,
    'bond_amount': None,
    'current_status': None,
    'court_dates': None,
    'days_jailed': None,
    'other': None,
    'notes': None,
    'arresting_agency': inmate['arrests'][0]['arrestingAgency'],
    'charge_description': inmate['charges'][0]['chargeDescription'],
    'jail_id': inmate['jailID'],
    'charge_count': inmate['chargeCount'],
    'so_num': inmate['defendantSONum']
  }

  inmate_list.append(inmate_dict)


# print(json.dumps(inmate_list, indent=2))

with open('dekalb.csv', 'w', newline='') as new_file:

  fieldnames = list(inmate_dict.keys())

  csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',', dialect='excel')

  csv_writer.writeheader()
  # csv_writer.writerow(fieldnames)

  for inmate in inmate_list:
    csv_writer.writerow(inmate)
  

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