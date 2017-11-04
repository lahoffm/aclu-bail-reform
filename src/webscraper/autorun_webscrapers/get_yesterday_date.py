# Called by batchfile to generate yesterday's date as argument to Dekalb webscraper
from datetime import datetime, timedelta

date_format = '%Y-%m-%d'
today = datetime.strptime(datetime.now().strftime(date_format), date_format)
yesterday = datetime.strftime(today + timedelta(days=-1), date_format)
print(yesterday)