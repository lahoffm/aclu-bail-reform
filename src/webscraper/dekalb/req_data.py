from fake_useragent import UserAgent

ua = UserAgent()

search_headers = {
  'content-type': 'application/json'
}

view_headers = {
  'User-Agent': str(ua.chrome)
}

search_payload = {
  "@odata.context":"https://it-odyint-wp2.dcg.dekalb.loc/app/JailSearchService/$metadata#search/$entity",
  "@odata.editLink":"http://search/fake",
  "Id":"0","queryString":"dkso",
  "from":10,
  "size":1,
  "facets":
    [
      {
        "name":"Date Booked",
        "type":"Date",
        "indexFieldName":"bookingDate",
        "displayOrder":1,
        "buckets":
          [
            {
              "name":"Past Year",
              "selected":False,
              "rangeFrom":"2016-10-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":7
            },
            {
              "name":"Past 3 Months",
              "selected":False,
              "rangeFrom":"2017-07-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":6
            },
            {
              "name":"Past Month",
              "selected":False,
              "rangeFrom":"2017-09-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":5
            },
            {
              "name":"Past Week",
              "selected":False,
              "rangeFrom":"2017-09-29T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":4
            },
            {
              "name":"Yesterday",
              "selected":False,
              "rangeFrom":"2017-10-05T00:00:00.000Z",
              "rangeTo":"2017-10-05T23:59:59.000Z",
              "displayOrder":3
            },
            {
              "name":"Custom",
              "selected":False,
              "rangeFrom":"2017-10-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T00:00:00.000Z",
              "displayOrder":1
            },
            {
              "name":"Today",
              "selected":False,
              "rangeFrom":"2017-10-09T00:00:00.000Z",
              "rangeTo":"2017-10-09T23:59:59.000Z",
              "displayOrder":2
            }
          ]
      },
      {
        "name":"Date Released",
        "type":"Date",
        "indexFieldName":"releaseDate",
        "displayOrder":2,
        "buckets":
          [
            {
              "name":"Past Year",
              "selected":False,
              "rangeFrom":"2016-10-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":7
            },
            {
              "name":"Past 3 Months",
              "selected":False,
              "rangeFrom":"2017-07-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":6
            },
            {
              "name":"Past Month",
              "selected":False,
              "rangeFrom":"2017-09-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":5
            },
            {
              "name":"Past Week",
              "selected":False,
              "rangeFrom":"2017-09-29T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z",
              "displayOrder":4
            },
            {
              "name":"Yesterday",
              "selected":False,
              "rangeFrom":"2017-10-05T00:00:00.000Z",
              "rangeTo":"2017-10-05T23:59:59.000Z",
              "displayOrder":3
            },
            {
              "name":"Custom",
              "selected":False,
              "rangeFrom":"2017-10-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T00:00:00.000Z",
              "displayOrder":1
            },
            {
              "name":"Today",
              "selected":False,
              "rangeFrom":"2017-10-06T00:00:00.000Z",
              "rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":2
            }
          ]
      }
    ],
  "parameters":{},
  "sorts":
    [
      {
        "name":"Booking Number",
        "indexFieldName":"bookingNumber.sort",
        "missingValueOrderFirst":False,
        "reverseOrder":False,
        "selected":False,
        "default":False
      },
      {
        "name":"Relevance",
        "indexFieldName":"_score",
        "missingValueOrderFirst":False,
        "reverseOrder":False,
        "selected":True,
        "default":True
      }
    ]
}