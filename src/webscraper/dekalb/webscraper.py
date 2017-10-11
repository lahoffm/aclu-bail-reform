import sys
import requests
import json
import csv
from nameparser import HumanName
import req_data as req
import parser_index as parser

if len(sys.argv) > 1:
  command = sys.argv[1]
  if command == 'all':
    if len(sys.argv) == 4:
      print('Please wait...')
      from_index = sys.argv[2]
      num_results = sys.argv[3]
      params = req.create_params(from_index=from_index, num_results=num_results)
      label = parser.get_cvs_label(command=command, from_index=from_index, num_results=num_results)
    else:
      print('Please specify a start index (min 0) and the number of wanted results (max 1000).')
      sys.exit()
  elif command == 'today':
    print('Please wait...')
    params = req.create_params(today=True)
    label = parser.get_cvs_label(command=command)
  elif command == 'custom':
    if len(sys.argv) == 3:
      print('Please wait...')
      custom_date = sys.argv[2]
      print(custom_date)
      params = req.create_params(today=True, custom_date=custom_date)
      label = parser.get_cvs_label(command=command, custom_date=custom_date)
    else:
      print('Please specify a date (yyyy-mm-dd).')
      sys.exit()
  else:
    print('Please enter a valid command (all, today).')
    sys.exit()
else:
  print('Please wait...')
  params = req.create_params()
  label = parser.get_cvs_label()

payload = req.get_payload(params)
req_post = requests.post('https://ody.dekalbcountyga.gov/app/JailSearchService/search', json=payload, headers=req.get_headers())
search_results = req_post.json()

if 'searchResult' not in search_results:
  print('Please input a valid date.')
  sys.exit()

inmate_data = list(search_results['searchResult']['hits'])

if len(inmate_data) == 0:
  print('No results found.')
  sys.exit()
inmate_list = []

i = 0

for inmate in inmate_data:
  name = HumanName(inmate['defendantName'])
  jail_id = str(inmate['jailID'])
  view_url = 'https://ody.dekalbcountyga.gov/app/ViewJailing/#/jailing/' + jail_id
  req_get = requests.get('https://ody.dekalbcountyga.gov/app/ViewJailingService//Jailings(' + jail_id + ')')

  print(req_get.content)

  if 'headers' in req_get:
    print(i)
    print(req_get.headers)
    i = i + 1
  else:
    print('not working')

  jailing_data = req_get.json()

  inmate_dict = {
    'county_name': 'dekalb',
    'timestamp': parser.get_current_timestamp(),
    'url': view_url,
    'inmate_id': inmate['bookingNumber'],
    'inmate_lastname': name.last,
    'inmate_firstname': name.first,
    'inmate_middlename': name.middle,
    'inmate_sex': jailing_data['DefendantGender'],
    'inmate_race': jailing_data['DefendantRace'],
    'inmate_age': parser.get_age(jailing_data['DefendantDOBString']),
    'inmate_dob': parser.get_dob_str(jailing_data['DefendantDOBString']),
    'inmate_address': ', '.join(jailing_data['DefendantAddress']),
    'booking_timestamp': parser.get_booking_timestamp(jailing_data['BookingDateString'], jailing_data['BookingTime']),
    'release_timestamp': parser.get_release_timestamp(jailing_data['ReleaseTime']),
    'processing_numbers': parser.get_ids_str(inmate['defendantSONum'], inmate['bookingNumber'], inmate['jailID'], inmate['arrests'][0]['arrestID']),
    'agency': inmate['arrests'][0]['arrestingAgency'],
    'facility': jailing_data['Facility'],
    'charges': parser.get_charges_str(jailing_data['Charges']),
    'severity': None,
    'bond_amount': None,
    'current_status': None,
    'court_dates': None,
    'days_jailed': parser.get_days_jailed(jailing_data['BookingDateString'], jailing_data['BookingTime']),
    'other': None,
    'notes': None
  }

  inmate_list.append(inmate_dict)

with open('./../../../data/dekalb-' + label + '-' + parser.get_csv_timestamp() + '.csv', 'w', newline='') as new_file:

  fieldnames = list(inmate_dict.keys())

  csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',', dialect='excel')

  csv_writer.writeheader()

  for inmate in inmate_list:
    csv_writer.writerow(inmate)

print('Scrape complete! (Check the data folder for dekalb-*.csv.)')