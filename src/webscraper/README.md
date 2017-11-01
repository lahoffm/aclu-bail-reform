Cobb County Jail Webscraper

This code was written in Python 3.6, and relies on packages requests, re, sys, csv, pandas, numpy, bs4, datetime, and math. All of these packages can installed via the pip install method. The code automatically uses the current date it is being run and 

submits the url to recieve the last three days of arrest records from cobb counties website.

Following lines of cobb_scrapper.py will need adjustment to the location you wish to have the file stored at:

Line 311    with open(r'C:\Users\Desktop\Cobb County\Cobb_'+stamp+'-'+full_time+'.csv', 'w') as csvfile: