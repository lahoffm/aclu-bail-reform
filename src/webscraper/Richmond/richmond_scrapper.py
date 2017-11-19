#!/usr/bin/python

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options  



#Prepare page for scrapping
def init_page():
    try:
            accept_button = driver.find_element_by_id("btnAccept")
            accept_button.click()

            recent_bookings_button = driver.find_element_by_id("btnRecent")
            recent_bookings_button.click()
    except NoSuchElementException as error:
            print("Error: {0}".format(error))
            exit()

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

#TODO: Extract the number of pages available to walk through
def get_booking_pages():
    return []

#TODO: Implement logic to navigate to the next page
#check if next page link is clickable, if it is, click and parse all the booking rows
#stop when next link is not clickable
def navigate_to_page(page_num):
    print("next page lol")

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

#Init Driver
options = Options()  
options.add_argument("headless")
options.add_argument("disable-gpu")  
options.add_argument("window-size=1200x600")  #Prevents "Element not clickable issue when running in headless mode"

driver = webdriver.Chrome(chrome_options=options)
driver.get("http://appweb2.augustaga.gov/InmateInquiry/AltInmatesOnline.aspx")

init_page()
row_link_ids = get_links_on_page()

for link_id in row_link_ids:
    #TODO: Fix issue where scrapping fails when in headless mode
    extract_inmate_info_from_page(link_id)

driver.close()
