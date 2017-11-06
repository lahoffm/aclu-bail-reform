import sys
import requests
import json
import csv
from datetime import datetime
from nameparser import HumanName
import req_data as req
import helpers_index as helpers

try:
  command = sys.argv[1]
except IndexError:
  print('Please enter a valid command (all, today, custom).')
  sys.exit()
else:
  if command == 'all':
    try:
      from_index = sys.argv[2]
      num_records = sys.argv[3]
    except IndexError:
      print('Please specify a start index (min 0) and the number of wanted records.')
      sys.exit()
    else:
      try:
        n = int(from_index)
        m = int(num_records)
        if n < 0: raise ValueError
        if m < 0: raise ValueError
      except ValueError:
        print('Index number and record size must be positive integers.')
        sys.exit()
      else:
        params = req.create_params(from_index=from_index, num_records=num_records)
        label = helpers.get_csv_label(command=command, from_index=from_index, num_records=num_records)
  elif command == 'today':
    params = req.create_params(today=True)
    label = helpers.get_csv_label(command=command)
  elif command == 'custom':
    try:
      custom_date = sys.argv[2]
    except IndexError:
      print('Please specify a date (yyyy-mm-dd).')
      sys.exit()
    else:
      try:
        valid = datetime.strptime(custom_date, '%Y-%m-%d')
      except Exception as e:
        print('Please input a valid date (yyyy-mm-dd).')
        sys.exit()
      else:
        params = req.create_params(today=True, custom_date=custom_date)
        label = helpers.get_csv_label(command=command, custom_date=custom_date)
  else:
    print('Please enter a valid command (all, today, custom).')
    sys.exit()

print('Scraping...')

payload = req.get_payload(params)
req_post = requests.post('https://ody.dekalbcountyga.gov/app/JailSearchService/search', json=payload, headers=req.get_headers())
search_results = req_post.json()

inmate_data = list(search_results['searchResult']['hits'])

if len(inmate_data) == 0:
  print('No records found.')
  sys.exit()

with open('./../../../data/dekalb_' + label + '.csv', 'w', newline='') as new_file:

  csv_writer = csv.DictWriter(new_file, fieldnames=helpers.fieldnames, delimiter=',', dialect='excel')

  csv_writer.writeheader()

  progress_count = 0

  invalid_ids = []

  for inmate in inmate_data:
    name = HumanName(inmate['defendantName'])
    jail_id = str(inmate['jailID'])
    view_url = 'https://ody.dekalbcountyga.gov/app/ViewJailing/#/jailing/' + jail_id
    req_get = requests.get('https://ody.dekalbcountyga.gov/app/ViewJailingService//Jailings(' + jail_id + ')')

    if name.suffix != '':
      suffix = ', ' + name.suffix
    else:
      suffix = name.suffix

    if req_get.headers['Content-Length'] == '0':
      invalid_ids.append(jail_id)
      continue

    jailing_data = req_get.json()
    # print(json.dumps(jailing_data, indent=2))
    charges = helpers.parse_charges(jailing_data['Charges'])

    inmate_dict = {
      'county_name': 'dekalb',
      'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' EST',
      'url': view_url,
      'inmate_id': inmate['bookingNumber'],
      'inmate_lastname': name.last,
      'inmate_firstname': name.first + suffix,
      'inmate_middlename': name.middle,
      'inmate_sex': helpers.parse_sex(jailing_data['DefendantGender']),
      'inmate_race': jailing_data['DefendantRace'],
      'inmate_age': helpers.get_age(jailing_data['DefendantDOBString']),
      'inmate_dob': helpers.get_dob_str(jailing_data['DefendantDOBString']),
      'inmate_address': ', '.join(jailing_data['DefendantAddress']),
      'booking_timestamp': helpers.parse_timestamp(jailing_data['BookingDateString'], jailing_data['BookingTime']),
      'release_timestamp': helpers.parse_timestamp(jailing_data['ReleaseDateString'], jailing_data['ReleaseTime']),
      'processing_numbers': helpers.get_ids_str(inmate['defendantSONum'], inmate['bookingNumber'], inmate['jailID'], inmate['arrests'][0]['arrestID']),
      'agency': inmate['arrests'][0]['arrestingAgency'],
      'facility': jailing_data['Facility'],
      'charges': ' | '.join(charges['desc']),
      'severity': ' | '.join(charges['sev']),
      'bond_amount': ' | '.join(charges['bond']),
      'current_status': ' | '.join(charges['disp']),
      'court_dates': None,
      'days_jailed': helpers.get_days_jailed(jailing_data['BookingDateString'], jailing_data['BookingTime'], jailing_data['ReleaseTime']),
      'other': None,
      'notes': None
    }

    csv_writer.writerow(inmate_dict)

    progress_count = progress_count + 1

    if command == 'all':
      print('Progress: ' + str(progress_count) + '/' + str(num_records), end='\r')
    else:
      print('Progress: ' + str(progress_count), end='\r')

print('Scrape complete!           ')
print('Total scraped: ' + str(progress_count) + ' record(s)')
if len(invalid_ids) > 0:
  print('We were unable to scrape for the following Jail ID(s): ' + ', '.join(invalid_ids))
print('Check the data folder for dekalb-*.csv.')