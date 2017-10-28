# Webscraper for Athens-Clarke county
* Python 3.6.3
* Retrieves records for [Athens-Clarke county jail](https://www.athensclarkecounty.com/938/Public-Records-Access)
* Uses [```pandas.read_html```](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_html.html)

# How to install and run
* Install [Anaconda](https://www.continuum.io/downloads), open command line
* Create new environment: ```conda create --name python_363 python=3.6.3```
* Activate environment on Windows: ```activate python_363```, Linux/macOS: ```source activate python_363```
* ```cd``` to the Athens-Clarke scraper directory, which contains [```requirements.txt```](requirements.txt)
* ```pip install -r requirements.txt```
* ```python webscraper_main.py``` - writes 2 CSV files into ```../../../data``` as specified in [CONTRIBUTING.md](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md)
* Makes 2 files because Athens-Clarke county has both "Current inmate roster" and "Arrests from last 7 days", which have somewhat different information.

## Results
[As per the specifications](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md#csv-columns-in-order), the resulting CSV includes the following columns:

| Column Name       | Data Available
|-------------------|---------------|
| county_name       | ✓ |
| timestamp         | ✓ |
| url               | ✓ |
| inmate_id         | ✓ |
| inmate_lastname   | ✓ |
| inmate_firstname  | ✓ |
| inmate_middlename | ✓ |
| inmate_sex        | ✓ |
| inmate_race       | ✓ |
| inmate_age        | ✓ |
| inmate_dob        | Year only |
| inmate_address    | ✓ |
| booking_timestamp | ✓ |
| release_timestamp | Only for booking-report csv |
| processing_numbers| ✓ |
| agency            | ✓ |
| facility          | ✓ |
| charges           | ✓ |
| severity          | ✓ |
| bond_amount       | ✓ |
| current_status    | ✓ |
| court_dates       | ✗ |
| days_jailed       | ✗ |
| other             | Only for booking-report csv: court jurisdiction & extra bond info |
| notes				| ✓ |