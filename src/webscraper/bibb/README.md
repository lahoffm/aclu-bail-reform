# Python Web Scraper
JailCrawler is a Python-based web scraper using [Scrapy](https://scrapy.org/).
It is developed to retrieve the records for Bibb County.

## Installation
### Create your virtual environment (optional)
It is recommended to use a virtual environment to manage project versions and dependencies.
Using [virtualenv](https://virtualenv.pypa.io/en/stable/installation/), create a virtual environment using Python 3.6.1+:
`virtualenv ucla-env -p <path to Python 3.6.1+ library>`

Then activate your virtual environment:
`source ucla-env/bin/activate`

### Install Scrapy
To install Scrapy follow [their installation guide for your system.](https://doc.scrapy.org/en/latest/intro/install.html)


## How to Use
### About Bibb County
Bibb County only allow for a scan on the current day's arrest records. The records are updated regularly throughout the day. Scans performed at the beginning of the day may update and new records are added. The page displaying the records will reset at midnight EST.

### Running the Spider
If you are using a virtual environment, make sure it is activated for your terminal instance.
1. Navigate to the `jailCrawler` folder.
2. Run the spider using the following command in the terminal: `scrapy crawl bibb`
3. The results will create a new CSV file named `bibb-output-<datetime>.csv` in the `output` folder.

### Results
[As per the specifications](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md#csv-columns-in-order), the resulting CSV includes the following columns:
| Column Name     | Data Available
|=================|===============|
county_name       | ✓
timestamp         | ✓
url               | ✓
inmate_id         | ✓
inmate_lastname   | ✓
inmate_firstname  | ✓
inmate_middlename | ✓
inmate_sex        | ✓
inmate_race       | ✓
inmate_age        | ✓
inmate_dob        | Year Only
inmate_address    | ✓
booking_timestamp | ✓
release_timestamp | ✓
processing_numbers| ✗
agency            | ✓
facility          | ✗
charges           | ✓
severity          | ✗
bond_amount       | ✓
current_status    | ✓
court_dates       | ✗
days_jailed       | ✗
other             | ✗
