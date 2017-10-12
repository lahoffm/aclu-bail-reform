from datetime import date, datetime
import agecalc
import re

def validate_int(index, size):
  try:
    val1 = int(index)
    val2 = int(size)
    if val1 > 0 and val2 > 0:
      return True
    else:
      return False
  except ValueError:
    return False

def validate_date(date_text):
  try:
    datetime.strptime(date_text, '%Y-%m-%d')
    return True
  except ValueError:
    return False

def get_current_timestamp():
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  dt,tm = re.split(' ', timestamp)
  return dt + ' ' + tm + ' EST'

def get_cvs_label(command='all', from_index='0', num_records='100', custom_date=None):
  if command == 'today':
    return 'TODAY'
  elif command == 'custom':
    return 'CUSTOM' + custom_date.replace('-', '')
  else:
    return 'ALLstart' + from_index + 'size' + num_records

def get_csv_timestamp():
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  date,time = re.split(' ', timestamp)
  y,mo,d = re.split('-', date)
  h,mi,s = re.split(':', time)
  return '_'.join([y, mo, d, h, mi, s])

def get_charges_str(charges):
  charges_list = []
  for charge in charges:
    charges_list.append(charge['ChargeDescription'])
  charges_str = ' | '.join(charges_list)
  return charges_str

def get_ids_str(so, booking, jail, arrest):
  return ' | '.join([
    'so#=' + str(so),
    'booking#=' + str(booking),
    'jail_id=' + str(jail),
    'arrest_id=' + str(arrest)
  ])

def get_dob_str(dob):
  if dob == None:
    return None
  else:
    m,d,y = re.split('/', dob)
    return date(int(y), int(m), int(d)).isoformat()

def get_age(dob):
  if dob == None:
    return None
  else:
    d,m,y = re.split('/', dob)
    calc = agecalc.AgeCalc(int(d), int(m), int(y))
    return calc.age

def get_booking_timestamp(date_string, time_string):
  m,d,y = re.split('/', date_string)
  dt = date(int(y), int(m), int(d)).isoformat()
  t_split = time_string.split('T')[1]
  tm = t_split.split('-')[0]
  return dt + ' ' + tm + ' EST'

def get_release_timestamp(release_string):
  dt,t_part = re.split('T', release_string)
  tm = t_part.split('-')[0]
  return dt + ' ' + tm + ' EST'

def get_days_jailed(date_string, time_string):
  ts = get_booking_timestamp(date_string, time_string)
  date,time,other = re.split(' ', ts)
  y,mo,d = re.split('-', date)
  h,mi,s = re.split(':', time)
  today = datetime.now()
  booking_date = datetime(int(y), int(mo), int(d), int(h), int(mi), int(s))
  return (today - booking_date).days

fieldnames = [
    'county_name',
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
    'court_dates',
    'days_jailed',
    'other',
    'notes'
  ]