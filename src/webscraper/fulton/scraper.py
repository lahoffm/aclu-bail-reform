from selenium import webdriver
from selenium.common import exceptions
#import os
from bs4 import BeautifulSoup

#dir_path = os.path.dirname(os.path.realpath(__file__))
#chrome_path = os.path.join(dir_path,"chromedriver")
#driver = webdriver.Chrome(chrome_path)
fulton_home = "http://justice.fultoncountyga.gov/PAJailManager/default.aspx"

def scrape(driver, search_record):
    scraped_record = []
    driver.get(fulton_home)
    driver.find_element_by_xpath("""/html/body/table/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/a""").click()
    driver.find_element_by_xpath("""//*[@id="BookingNumberOption"]""").click()
    elem = driver.find_element_by_xpath("""//*[@id="BookingNumber"]""")
    elem.send_keys(str(search_record))
    driver.find_element_by_xpath("""//*[@id="SearchSubmit"]""").click()
    try:
        driver.find_element_by_xpath("""/html/body/table[4]/tbody/tr[3]/td[1]/a""").click()
        record_source = driver.page_source    
        record_soup = BeautifulSoup(record_source, 'html.parser')
        main_content = record_soup.find(id="MainContent")
        try:
            tables = main_content.find_all('table')
        except AttributeError:
            print(str(search_record)," is redacted")
            return scraped_record
        data = []
        for table in tables:
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols])
        scraped_record = data
        print("scraped: ",search_record)
    except exceptions.NoSuchElementException:
        print("could not scrape: ",str(search_record))
    return scraped_record
