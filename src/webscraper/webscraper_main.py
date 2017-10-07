# will be webscraping code
# from urllib.request import urlopen as uReq
# from bs4 import BeautifulSoup as soup

# my_url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20cards'

# # opening up connection, grabbing the page
# uClient = uReq(my_url)
# page_html = uClient.read()
# uClient.close()

# # html parsing
# page_soup = soup(page_html, "html.parser")

# #grabs each product
# containers = page_soup.findAll("div", {"class": "item-container"})

# filename = "products.csv"
# f = open(filename, "w")

# headers = "brand, product_name, shipping\n"

# f.write(headers)

# for container in containers:
#   brand = container.div.div.a.img["title"]

#   title_container = container.findAll("a", {"class": "item-title"})
#   product_name = title_container[0].text

#   shipping_container = container.findAll("li", {"class": "price-ship"})
#   shipping = shipping_container[0].text.strip()

#   print("brand: " + brand)
#   print("product_name: " + product_name)
#   print("shipping: " + shipping)

#   f.write(brand + " , " + product_name.replace(",", "|") + " ," + shipping + "\n")

#   f.close()

import requests
import json

url = 'https://ody.dekalbcountyga.gov/app/JailSearchService/search'
headers = {'content-type': 'application/json'}
payload = {"@odata.context":"https://it-odyint-wp2.dcg.dekalb.loc/app/JailSearchService/$metadata#search/$entity","@odata.editLink":"http://search/fake","Id":"0","queryString":"dkso","from":0,"size":1,"facets":[{"name":"Date Booked","type":"Date","indexFieldName":"bookingDate","displayOrder":1,"buckets":[{"name":"Past Year","count":22071,"selected":False,"rangeFrom":"2016-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":7},{"name":"Past 3 Months","count":6421,"selected":False,"rangeFrom":"2017-07-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":6},{"name":"Past Month","count":2394,"selected":False,"rangeFrom":"2017-09-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":5},{"name":"Past Week","count":589,"selected":False,"rangeFrom":"2017-09-29T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":4},{"name":"Yesterday","count":92,"selected":False,"rangeFrom":"2017-10-05T00:00:00.000Z","rangeTo":"2017-10-05T23:59:59.000Z","displayOrder":3},{"name":"Custom","count":0,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T00:00:00.000Z","displayOrder":1},{"name":"Today","count":27,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":2}]},{"name":"Date Released","type":"Date","indexFieldName":"releaseDate","displayOrder":2,"buckets":[{"name":"Past Year","count":22240,"selected":False,"rangeFrom":"2016-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":7},{"name":"Past 3 Months","count":6468,"selected":False,"rangeFrom":"2017-07-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":6},{"name":"Past Month","count":2443,"selected":False,"rangeFrom":"2017-09-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":5},{"name":"Past Week","count":562,"selected":False,"rangeFrom":"2017-09-29T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":4},{"name":"Yesterday","count":106,"selected":False,"rangeFrom":"2017-10-05T00:00:00.000Z","rangeTo":"2017-10-05T23:59:59.000Z","displayOrder":3},{"name":"Custom","count":0,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T00:00:00.000Z","displayOrder":1},{"name":"Today","count":15,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":2}]}],"parameters":{},"sorts":[{"name":"Booking Number","indexFieldName":"bookingNumber.sort","missingValueOrderFirst":False,"reverseOrder":False,"selected":False,"default":False},{"name":"Relevance","indexFieldName":"_score","missingValueOrderFirst":False,"reverseOrder":False,"selected":True,"default":True}]}

req_post = requests.post(url, json=payload, headers=headers)

data = req_post.json()

dataList = data['searchResult']['hits']

print(json.dumps(data['searchResult']['hits'][0], indent=2))

inmate = dataList[0]

print('Type: ' + inmate[])
print('Booking Number: ' + dataList[0])

# payload1 = {"@odata.context":"https://it-odyint-wp2.dcg.dekalb.loc/app/JailSearchService/$metadata#search/$entity","@odata.editLink":"http://search/fake","Id":"0","queryString":"dkso","from":100000,"size":100000,"facets":[{"name":"Date Booked","type":"Date","indexFieldName":"bookingDate","displayOrder":1,"buckets":[{"name":"Past Year","count":22071,"selected":False,"rangeFrom":"2016-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":7},{"name":"Past 3 Months","count":6421,"selected":False,"rangeFrom":"2017-07-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":6},{"name":"Past Month","count":2394,"selected":False,"rangeFrom":"2017-09-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":5},{"name":"Past Week","count":589,"selected":False,"rangeFrom":"2017-09-29T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":4},{"name":"Yesterday","count":92,"selected":False,"rangeFrom":"2017-10-05T00:00:00.000Z","rangeTo":"2017-10-05T23:59:59.000Z","displayOrder":3},{"name":"Custom","count":0,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T00:00:00.000Z","displayOrder":1},{"name":"Today","count":27,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":2}]},{"name":"Date Released","type":"Date","indexFieldName":"releaseDate","displayOrder":2,"buckets":[{"name":"Past Year","count":22240,"selected":False,"rangeFrom":"2016-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":7},{"name":"Past 3 Months","count":6468,"selected":False,"rangeFrom":"2017-07-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":6},{"name":"Past Month","count":2443,"selected":False,"rangeFrom":"2017-09-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":5},{"name":"Past Week","count":562,"selected":False,"rangeFrom":"2017-09-29T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":4},{"name":"Yesterday","count":106,"selected":False,"rangeFrom":"2017-10-05T00:00:00.000Z","rangeTo":"2017-10-05T23:59:59.000Z","displayOrder":3},{"name":"Custom","count":0,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T00:00:00.000Z","displayOrder":1},{"name":"Today","count":15,"selected":False,"rangeFrom":"2017-10-06T00:00:00.000Z","rangeTo":"2017-10-06T23:59:59.000Z","displayOrder":2}]}],"parameters":{},"sorts":[{"name":"Booking Number","indexFieldName":"bookingNumber.sort","missingValueOrderFirst":False,"reverseOrder":False,"selected":False,"default":False},{"name":"Relevance","indexFieldName":"_score","missingValueOrderFirst":False,"reverseOrder":False,"selected":True,"default":True}]}

# r1 = requests.post(url, json=payload, headers=headers)
# print(r1.json())