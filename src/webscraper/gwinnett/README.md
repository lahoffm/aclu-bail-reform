# Python Web Scraper
This is a Python-based web scraper using [Scrapy](https://scrapy.org/).
It is developed to retrieve the records for [Gwinnett County](http://www.gwinnettcountysheriff.com),
["Docket Book" menu item](http://www.gwinnettcountysheriff.com/smartwebclient/)

## Installation
### Create your virtual environment (optional)
It is recommended to use a virtual environment to manage project versions and dependencies.
Using [virtualenv](https://virtualenv.pypa.io/en/stable/installation/), create a virtual environment using Python 3.6.1+:
`virtualenv <env name> -p <path to Python 3.6.1+ library>`

Then activate your virtual environment:
`source <env name>/bin/activate`

### Install Scrapy and pandas
To install Scrapy follow [their installation guide for your system](https://doc.scrapy.org/en/latest/intro/install.html).

## How to Use
### About Gwinnett County
Gwinnett County allows users to search for current inmates, released inmates, or both by name or booking date. The default search is bookings in the last 24 hours. The results page is paginated via a "Load More Results" button that appears at the end of the listings.

### Running the Spider
If you are using a virtual environment, make sure it is activated for your terminal instance.
1. Navigate to the `gwinnett` folder.
2. Run the spider using the following command in the terminal: `` scrapy crawl gwinnettsmartweb -o ../../../data/gwinnett_`date +%Y-%m-%d_%H-%M-%S`.csv ``
3. The results will create a new CSV file named `gwinnett_<datetime>.csv` in the `../../../data` folder.

### Results
[As per the specifications](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md#csv-columns-in-order), the resulting CSV includes the following columns:

| Column Name       | Data Available
|-------------------|---------------|
| county_name       | ✓ |
| timestamp         | ✓ |
| url               | ✓ |
| inmate_id         | ✗ |
| inmate_lastname   | ✓ |
| inmate_firstname  | ✓ |
| inmate_middlename | Combined in inmate_firstname |
| inmate_sex        | ✓ |
| inmate_race       | For some inmates |
| inmate_age        | ✓ |
| inmate_dob        | ✗ |
| inmate_address    | ✓ |
| booking_timestamp | ✓ |
| release_timestamp | ✗ |
| processing_numbers| ✗ |
| agency            | ✗ |
| facility          | ✓ |
| charges           | ✓ |
| severity          | For some charges |
| bond_amount       | ✓ |
| current_status    | ✓ |
| court_dates       | ✗ |
| days_jailed       | ✗ |
| other             |  |
| notes				|  |