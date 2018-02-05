#!/usr/bin/python

from datetime import datetime
import time
import collections
import csv
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

InmateExtract = collections.namedtuple("InmateExtract", ["booking_number", "full_name", "arrest_date", "race", "sex", "age", "charges", "charges_bond", "charges_status"])
columns =  ["county_name", "timestamp", "url", 
    "inmate_id", "inmate_lastname", "inmate_firstname", "inmate_middlename",
    "inmate_sex", "inmate_race", "inmate_age", "inmate_dob", "inmate_address",
    "booking_timestamp", "release_timestamp", "processing_numbers",
    "agency", "facility", "charges", "severity", "bond_amount", "current_status",
    "court_dates", "days_jailed", "other", "notes"]
Inmate = collections.namedtuple("Inmate", columns)

#Prepare page for scrapping
def init_page():
    try:
        accept_button = driver.find_element_by_id("btnAccept")
        accept_button.click()

        recent_bookings_button = driver.find_element_by_id("btnRecent")
        recent_bookings_button.click()
    except NoSuchElementException as error:
            print("Error: {0}".format(error))
            

    for try_attempt in range(0, 3):
        try:
            select = Select(driver.find_element_by_name("ddlPerPage2"))
            row_options = select.options
            largest_option = row_options[0]

            for option in select.options:
                if int(largest_option.get_attribute("value")) < int(option.get_attribute("value")):
                    largest_option = option
            select.select_by_value(largest_option.get_attribute("value"))
            print("Picked", largest_option.get_attribute("value"), "as the largest option")
        except NoSuchElementException as error:
            print("Error: {0}".format(error))
            exit()
        except StaleElementReferenceException:
            print("Dom updated, retrying page preparation")
            continue
        break

def navigate_to_next_page():
    for try_attempt in range(0, 3):
        try:
            next_page_link = driver.find_element_by_id("Pager1_lbnForeOne")

            if next_page_link.get_attribute("class") == "aspNetDisabled":
                return False

            next_page_link.click()
            time.sleep(2)
        except NoSuchElementException as error:
            print("Error: {0}".format(error))
            exit()
        except StaleElementReferenceException:
            print("Dom updated, retrying click")
            continue
        print("Navigated to next page")
        return True

def get_links_on_page():
    row_link_ids = []
    for try_attempt in range(0, 2):

        try:
            row_links = driver.find_elements_by_css_selector("div.inmpanel > table > tbody > tr > td:first-child > a.poplink")
            row_link_ids = list(map(lambda x: x.get_attribute("id"), row_links))
        except StaleElementReferenceException:
            print("Dom updated, trying to get all link IDs again")
            continue
        break
    print("Found", len(row_link_ids), "links on page")
    return row_link_ids

#Begin Scrapping

def extract_inmate_info_from_page(row_link_id):
    booking_number = ""
    full_name = ""
    arrest_date = ""
    race = ""
    sex = ""
    age = ""
    charges = []
    charges_bond = []
    charges_status = []

    #Click on inmate
    for try_attempt in range(0, 3):
        try:
            
            row_link_elem = driver.find_element_by_id(row_link_id)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, row_link_id)))
            row_link_elem.click()
        except NoSuchElementException as error:
            print("Error: {0}".format(error))
            exit()
        except StaleElementReferenceException:
            print("Dom updated, retrying click")
            continue
        break

    #Grab info
    for attempt in range(0, 3):
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of(driver.find_element_by_id("mpeDetail_foregroundElement")))

            booking_number = driver.find_element_by_id("lblBKNo").get_attribute("innerText") 
            full_name = driver.find_element_by_id("InmateData1_lblFullName").get_attribute("innerText")
            arrest_date = driver.find_element_by_id("InmateData1_lblArrDt").get_attribute("innerText")
            race = driver.find_element_by_id("InmateData1_lblRace").get_attribute("innerText")
            sex = driver.find_element_by_id("InmateData1_lblSex").get_attribute("innerText")
            age = driver.find_element_by_id("InmateData1_lblAge").get_attribute("innerText")

            charge_rows = driver.find_elements_by_css_selector("table#InmateData1_dlChgs > tbody > tr")
            charge_rows_count = len(charge_rows) - 1 #Subtract column header
            for charge_num in range(0, charge_rows_count):
                charge_selector = "InmateData1_dlChgs_lblChg_{0}".format(charge_num)
                charge_bond_selector = "InmateData1_dlChgs_lblBondAmt_{0}".format(charge_num)
                charge_status_selector = "InmateData1_dlChgs_lblDisp_{0}".format(charge_num)

                charge = driver.find_element_by_id(charge_selector).get_attribute("innerText")
                charge_bond = driver.find_element_by_id(charge_bond_selector).get_attribute("innerText")
                charge_status = driver.find_element_by_id(charge_status_selector).get_attribute("innerText")
                
                charges.append(charge)
                charges_bond.append(charge_bond)
                charges_status.append(charge_status)
        except StaleElementReferenceException:
            #print("Dom updated, trying again")
            continue
        break

    #Close detail modal
    for try_attempt in range(0, 3):
        try:
            close_button = driver.find_element_by_id("btnClose")
            WebDriverWait(driver, 10).until(EC.visibility_of(close_button))
            close_button.click()
        except NoSuchElementException as error:
            print("Error: {0}".format(error))
            exit()
        except StaleElementReferenceException:
            print("Dom updated, retrying click")
            continue
        break

    inmate = InmateExtract(
        booking_number=booking_number,
        full_name=full_name,
        arrest_date=arrest_date,
        race=race,
        sex=sex,
        age=age,
        charges=charges,
        charges_bond=charges_bond,
        charges_status=charges_status
        )
    return inmate

def to_csv(inmate_extracts):
    date = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    dir_ = '../../../data'
    filename = dir_ + "/richmond_recent-bookings_{}.csv".format(date)
    with open(filename, "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(columns)

        for inmate in inmate_extracts:
            lastname = ""
            firstname = ""
            middlename = ""
            age = ""

            try:
                m = re.search("([a-zA-Z\s\-\'\"]+),\s([a-zA-Z\-\'\"]+)\s?([a-zA-Z\-\'\"]+)", inmate.full_name)
                lastname = m.group(1)
                firstname = m.group(2)

                #First name probably contains a middle name
                if len(m.groups()) > 2:
                    middlename = m.group(3)
            except AttributeError:
                print("Regex for name failed to match:", inmate.full_name)
                exit()
            
            try:
                m = re.search("(\d+)", inmate.age)
                age = m.group(1)
            except AttributeError:
                print("Regex for age failed:", inmate.age)
                exit()

            county_name = "richmond"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')
            url = "http://appweb2.augustaga.gov/InmateInquiry/AltInmatesOnline.aspx"
            inmate_id = ""
            inmate_lastname = lastname
            inmate_firstname = firstname
            inmate_middlename = middlename
            inmate_sex = inmate.sex.lower()[0] 
            inmate_race = inmate.race.lower()
            inmate_age = age
            inmate_dob = ""
            inmate_address = ""
            booking_timestamp = datetime.strptime(inmate.arrest_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            release_timestamp = ""
            processing_numbers = inmate.booking_number
            agency = "Richmond County Sheriff's Office"
            facility = ""
            charges = " | ".join(inmate.charges)
            severity = ""
            bond_amount = " | ".join(inmate.charges_bond)
            current_status = " | ".join(inmate.charges_status)
            court_dates = ""
            days_jailed = ""
            other = ""
            notes = ""

            writer.writerow([
                county_name,
                timestamp,
                url,
                inmate_id,
                inmate_lastname,
                inmate_firstname,
                inmate_middlename,
                inmate_sex,
                inmate_race,
                inmate_age,
                inmate_dob,
                inmate_address,
                booking_timestamp,
                release_timestamp,
                processing_numbers,
                agency,
                facility,
                charges,
                severity,
                bond_amount,
                current_status,
                court_dates,
                days_jailed,
                other,
                notes
                ])
    print("Generated CSV")



#Init Driver
options = Options()
options.add_argument("headless")
options.add_argument("disable-gpu")
#Prevents "Element not clickable issue when running in headless mode"
options.add_argument("window-size=1200x600")

driver = webdriver.Chrome(executable_path="./chromedriver.exe", chrome_options=options)
driver.get("http://appweb2.augustaga.gov/InmateInquiry/AltInmatesOnline.aspx")

init_page()

extracts = []

while True:
    for link_id in get_links_on_page():
       inmate_extract = extract_inmate_info_from_page(link_id)
       extracts.append(inmate_extract)
    if not navigate_to_next_page():
        break

driver.quit()

to_csv(extracts)
