import requests
import json
import req_data

base_url = 'https://ody.dekalbcountyga.gov'

search_url = base_url + '/app/JailSearchService/search'

req_post = requests.post(search_url, json=req_data.search_payload, headers=req_data.search_headers)

data = req_post.json()

inmate_list = data['searchResult']['hits']

inmate = inmate_list[0]

view_url = base_url + inmate['webIntents'][0]['uri']

print(req_data.view_headers)

inmate_dict = {
  'inmate_type': inmate['type'],
  'booking_date': inmate['bookingDate'],
  'booking_number': inmate['bookingNumber'],
  'arrest_id': inmate['arrests'][0]['arrestID'],
  'arresting_agency': inmate['arrests'][0]['arrestingAgency'],
  'charge_description': inmate['charges'][0]['chargeDescription'],
  'inmate_dob': inmate['defendantDOB'],
  'inmate_name': inmate['defendantName'],
  'facility': inmate['facility'],
  'jail_id': inmate['jailID'],
  'release_date': inmate['releaseDate'],
  'charge_count': inmate['chargeCount'],
  'booking_time': inmate['bookingTime'],
  'release_time': inmate['releaseTime'],
  'so_num': inmate['defendantSONum'],
  'uri': view_url
}

message = '''
SO#: {so_num}
Name: {inmate_name}
First Name: 
Last Name: 
Middle Name: 
Sex: 
Race: 
Age: 
Address: 
Bond Amount: 
DOB: {inmate_dob}
Facility: {facility}
Jail ID: {jail_id}
Arrest ID: {arrest_id}
Booking Number: {booking_number}
Booking Date: {booking_date}
Booking Time: {booking_time}
Type: {inmate_type}
Arresting Agency: {arresting_agency}
Charge Count: {charge_count}
Charge Description: {charge_description}
Release Date: {release_date}
Release Time: {release_time}
URI: {uri}
'''.format(**inmate_dict)

print(message) 



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