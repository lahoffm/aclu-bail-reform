#!/usr/bin/python

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

driver = webdriver.Chrome()
driver.get("http://appweb2.augustaga.gov/InmateInquiry/AltInmatesOnline.aspx")

try:
    accept_button = driver.find_element_by_id("btnAccept")
    accept_button.click()

    recent_bookings_button = driver.find_element_by_id("btnRecent")
    recent_bookings_button.click()
except NoSuchElementException as error:
    print("Error: {0}".format(error))
    exit()


row_links = driver.find_elements_by_css_selector("div.inmpanel > table > tbody > tr > td:first-child > a.poplink")

booking_number = ""
full_name = ""
arrest_date = ""
race = ""
sex = ""
age = ""
charges = []
charges_bond = []
charges_status = []

for try_attempt in range(0, 2):
    try:

        row_link = row_links[0]
        row_link_elem = driver.find_element_by_css_selector("a#dlList_lbnLName_0") 
        row_link_elem.click()
        
    except NoSuchElementException as error:
        print("Error: {0}".format(error))
        exit()
    except StaleElementReferenceException:
        print("Dom updated, retrying click")
        continue
    break


for attempt in range(0, 3):
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of(driver.find_element_by_id("mpeDetail_foregroundElement")))

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
        print("Dom updated, trying again")
        continue
    break

print(booking_number, full_name, arrest_date, race, sex, age)
print(charges)
print(charges_bond)
print(charges_status)

# county_name = "Richmond"
# timestamp = datetime.now()
# url = "http://appweb2.augustaga.gov/InmateInquiry/AltInmatesOnline.aspx"
# inmate_id = ""
# inmate_lastname = ""
# inmate_firstname = ""

#parse all rows

#check if next page link is clickable, if it is, click and parse all the booking rows
#stop when next link is not clickable

driver.close()
