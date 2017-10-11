from datetime import date

def create_params(from_index=0, num_results=100, today=False, custom_date=str(date.today())):
  params = {
    'from_index': from_index,
    'num_results': num_results,
    'today': today,
    'custom_date': custom_date
  }
  return params

def get_headers():
  headers = {
    'content-type': 'application/json'
  }
  return headers

def get_payload(params):
  payload = {
    '@odata.context':'https://it-odyint-wp2.dcg.dekalb.loc/app/JailSearchService/$metadata#search/$entity',
    '@odata.editLink':'http://search/fake',
    'Id':'0','queryString':'dkso',
    'from': params['from_index'],
    'size': params['num_results'],
    'facets':
      [
        {
          'name':'Date Booked',
          'type':'Date',
          'indexFieldName':'bookingDate',
          'displayOrder':1,
          'buckets':
            [
              {
                'name':'Today',
                'selected': params['today'],
                'rangeFrom': params['custom_date'] + 'T00:00:00.000Z',
                'rangeTo': params['custom_date'] + 'T23:59:59.000Z',
                'displayOrder':1
              }
            ]
        },
        {
          'name':'Date Released',
          'type':'Date',
          'indexFieldName':'releaseDate',
          'displayOrder':1,
          'buckets': []
        }
      ],
    'parameters':{},
    'sorts':
      [
        {
          'name':'Booking Number',
          'indexFieldName':'bookingNumber.sort',
          'missingValueOrderFirst':False,
          'reverseOrder':False,
          'selected':True,
          'default':True
        }
      ]
  }
  return payload