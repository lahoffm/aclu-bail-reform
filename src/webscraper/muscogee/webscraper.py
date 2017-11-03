"""
The url has changed on me before, so it might be good to change this
so it navigates to the same place from a stable url.
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from operator import itemgetter
from time import gmtime, strftime
from datetime import date
import csv

#PUT YOUR CHROME DRIVER PATH HERE
chrome_path = r""
if chrome_path == "":
    print("Paste chrome system path into the 'chrome_path' variable in order to run the program")
    
    

#opens chrome to grab html at url
#uses chrome because urllib gets ssl errors
def get_html(url):
    browser = webdriver.Chrome(chrome_path)
    browser.get(url)
    html = browser.page_source
    browser.quit()
    return html
    
def scrape_muscogee_docket(url, isIntake):
    all_entries = []
    url = get_html(url)
    soup = BeautifulSoup(url, 'html.parser')
    tables = soup.find_all('table')[1:-1]
    for table in tables:
        fonts = table.find_all('font')
        tags_content = []
        data = []
        for font in fonts:
            tags_content += [font.contents[0]]        
        if isIntake:
            if len(tags_content)>12:
                data = [""] + list(itemgetter(1,3,6,8,10,12)(tags_content))
        else:
            if len(tags_content)>14:
                data = list(itemgetter(1,3,5,8,10,12,14)(tags_content))
        all_entries += [data]
        
    return all_entries

#CSV Functions -------------------------------------------------------

fieldnames = ["county_name",        #'Muscogee'
              "timestamp",          #postgre_timestamp(timezone = True)
              "url",
              "inmate_id",
              "inmate_lastname",    #name_seperation(entry[2])[2]
              "inmate_firstname",   #name_seperation(entry[2])[0]
              "inmate_middlename",  #name_seperation(entry[2])[1]
              "inmate_sex",         #entry[5].lower()
              "inmate_race",        #parse_race(entry[4])
              "inmate_age",         #age(entry[3])
              "inmate_dob",         #entry[3]
              "inmate_address",
              "booking_timestamp",  #convert_timestamp(entry[1])
              "release_timestamp",  #convert_timestamp(entry[0])
              "processing_numbers",
              "agency",
              "facility",
              "charges",            #entry[6].replace(';',' | ')
              "severity",
              "bond_amount",
              "current_status",
              "court_dates",
              "days_jailed",
              "other",
              "notes"]

def muscogee_to_csv(data, isIntake, url, notes = ""):
    datatype = "release"
    if isIntake: datatype = "intake"
    with open("muscogee_" + datatype + "_" + postgre_timestamp().replace(":","-") + ".csv",
              "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for entry in data:
            #Maybe put this part in its own function
            name = name_seperation(entry[2])
            writer.writerow({'county_name': 'Muscogee',
                             'timestamp': postgre_timestamp(timezone = True),
                             'url': url,
                             'inmate_lastname': name[2],
                             'inmate_firstname': name[0],
                             'inmate_middlename': name[1],
                             'inmate_sex': entry[5].lower(),
                             'inmate_race': parse_race(entry[4]),
                             'inmate_age': age(entry[3]),
                             'inmate_dob': entry[3],
                             'booking_timestamp': convert_timestamp(entry[1]),
                             'release_timestamp': convert_timestamp(entry[0]),
                             'charges': entry[6].replace(';', ' | '),
                             'notes': notes})
              

def postgre_timestamp(timezone = False):
    timestamp = strftime("%Y-%m-%d_%H:%M:%S")
    if timezone:
        #hardcoded timezone because abbreviated zones are not standard
        #TODO: check for american timezones and return correct abbreviated timezone
        return timestamp + " EST"  
    else: return timestamp

def convert_timestamp(timestamp):
    s = timestamp.split("/")
    if len(s) == 3: return s[2] + "-" + s[0] + "-" + s[1]
    else: return ""

def name_seperation(full_name):
    split_name = full_name.rstrip().split(" ")
    if len(split_name) >= 3: return [split_name[0], split_name[1], split_name[-1]]
    else: return ["","",""]

def age(birth_year):
    return str((date.today().year+1)-int(birth_year))

def parse_race(r):
    if r == "W": return "white"
    elif r == "B": return "black"
    else: return "" #no other races used in muscogee 
#------------------------------------------------------------------------

def main():
    url = "https://ccg-domino9.columbusga.org/appl/MCSOJailInmateInformation.nsf/Web14DayIntake?OpenView&Start=11&Count=99999"
    data = scrape_muscogee_docket(url, True)
    muscogee_to_csv(data, True, url)
    url = "https://ccg-domino9.columbusga.org/appl/MCSOJailInmateInformation.nsf/Web14DayRelease?OpenView&Start=1&Count=99999"
    data = scrape_muscogee_docket(url, False)
    muscogee_to_csv(data, False, url)


main()
    
