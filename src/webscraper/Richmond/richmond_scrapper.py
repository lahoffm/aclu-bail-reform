#!/usr/bin/python

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

booking_rows = soup.find_all("div", class_ = "inmpanel")

#test
first_row = booking_rows[0]
row_link = first_row.find("a", class_="poplink")
row_link_id = row_link["id"]

try:
    row_link_elem = driver.find_element_by_id(row_link_id)
    row_link_elem.click()

    
except NoSuchElementException as error:
    print("Error: {0}".format(error))
    exit()

WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "InmateData1_pnlInmate")))


updated_soup = BeautifulSoup(driver.page_source, "html.parser")
detail_panel = updated_soup.find(id="pnlDetail")

print(detail_panel.find("div", id="InmateData1_pnlInmate"))
#test

#parse all rows

#check if next page link is clickable, if it is, click and parse all the booking rows
#stop when next link is not clickable

#driver.close()
