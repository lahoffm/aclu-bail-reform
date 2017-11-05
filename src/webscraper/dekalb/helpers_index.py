from datetime import date, datetime
import agecalc
import re

def get_csv_label(command='all', from_index='0', num_records='100', custom_date=None):
  current_ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  if command == 'today':
    return 'TODAY_' + current_ts
  elif command == 'custom':
    return 'CUSTOM' + custom_date.replace('-', '') + '_' + current_ts
  else:
    return 'ALLstart' + from_index + 'size' + num_records + '_' + current_ts

def parse_sex(sex):
  if sex == 'Male':
    return 'm'
  elif sex == 'Female':
    return 'f'
  else:
    return None

def parse_charges(charges):
  charges_dict = {
    'desc': [],
    'sev': [],
    'disp': [],
    'bond': []
  }
  terms = {
    'misd': ['MISD', 'MISDEMEANOR', 'misd', 'misdemeanor'],
    'fel': ['FEL', 'FELONY', 'fel', 'felony'],
    'fel&misd': ['FEL/MISD', 'F/M', 'fel/misd', 'f/m']
  }
  for charge in charges:
    charge_desc = charge['ChargeDescription']

    charges_dict['desc'].append(charge_desc)
    if any(words in charge_desc for words in terms['misd'] + terms['fel'] + terms['fel&misd']):
      if any(words in charge_desc for words in terms['fel&misd']):
        charges_dict['sev'].append('felony&misdemeanor')
      elif any(words in charge_desc for words in terms['misd']):
        charges_dict['sev'].append('misdemeanor')
      elif any(words in charge_desc for words in terms['fel']):
        charges_dict['sev'].append('felony')
    else:
      charges_dict['sev'].append(' ')

    if charge['Disposition'] == None:
      charges_dict['disp'].append(' ')
    else:
      charges_dict['disp'].append(charge['Disposition'])

    if charge['BondType'] == None:
      charges_dict['bond'].append(' ')
    else:
      charges_dict['bond'].append(charge['BondType'])

  return charges_dict


def get_ids_str(so, booking, jail, arrest):
  return ' | '.join([
    'SO# ' + str(so),
    'Booking Number ' + str(booking),
    'Jail ID' + str(jail),
    'Arrest ID ' + str(arrest)
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
  if release_string.startswith('0001') or release_string.startswith('1900'):
    return None
  else:
    dt,t_part = re.split('T', release_string)
    tm = t_part.split('-')[0]
    return dt + ' ' + tm + ' EST'

def get_days_jailed(book_date_str, book_time_str, release_str):
  book_ts = get_booking_timestamp(book_date_str, book_time_str)
  book_dt,book_tm,other = re.split(' ', book_ts)
  book_y,book_mo,book_d = re.split('-', book_dt)
  book_h,book_mi,book_s = re.split(':', book_tm)

  start_date = datetime(int(book_y), int(book_mo), int(book_d), int(book_h), int(book_mi), int(book_s))

  if release_str.startswith('0001') or release_str.startswith('1900'):

    end_date = datetime.now()

  else:
    rel_ts = get_release_timestamp(release_str)
    rel_dt,rel_tm,other = re.split(' ', rel_ts)
    rel_y, rel_mo, rel_d = re.split('-', rel_dt)
    rel_h, rel_mi, rel_s = re.split(':', rel_tm)

    end_date = datetime(int(rel_y), int(rel_mo), int(rel_d), int(rel_h), int(rel_mi), int(rel_s))

  return (end_date - start_date).days

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