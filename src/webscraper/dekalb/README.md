# Webscraper for Dekalb County Jail Records

This Python-based web scraper scrapes Dekalb County jail records from the [Dekalb County - Judicial Information System](https://ody.dekalbcountyga.gov/app/JailSearch/#/search) website.

The purpose of this project is to help build a case for the [ACLU Bail Reform Project](file:///C:/Users/Jieun/Downloads/ACLU-Bail-Reform-One-pager.pdf) in Georgia.

## Installing Requirements

- Python 3.6.3

```
pip install -r requirements.txt
```

Required packages are listed in **requirements.txt**.

## Commands & Usage

The following commands create a CSV file (*dekalb-\*.csv*) in the **data** folder. Jail records are sorted by inmate booking number. An inmate may have duplicate records if there are multiple charges. 

#### Default
`
python webscraper.py
`
By default, this command scrapes records starting from index 0 for 100 results.

#### Today
`
python webscraper.py today
`
This command scrapes all records, if any, for the current day (*e.g. 2017-10-01T00:00:00.000Z-2017-10-01T23:59:59.000Z*). If this command is used before any inmate booking, it will respond with 'No results found.'

#### Custom Date
`
python webscraper.py custom 1900-01-01
`
This comand scrapes all records for a custom date. The custom date must be specified as an argument in YYYY-MM-DD format. If there are no records for a specified date, it will respond with 'No resuts found.'

#### All Records
`
python webscraper.py all 0 100
`
This command scrapes records starting from an index number for a specified number of results.

| Column Name       | Data Available
|-------------------|---------------|
| county_name       | ✓ |
| timestamp         | ✓ |
| url               | ✓ |
| inmate_id<sup>1</sup>         | ✓ |
| inmate_lastname   | ✓ |
| inmate_firstname  | ✓ |
| inmate_middlename | ✓ |
| inmate_sex        | ✓ |
| inmate_race       | ✓ |
| inmate_age        | ✓ |
| inmate_dob        | ✓ |
| inmate_address    | ✓ |
| booking_timestamp | ✓ |
| release_timestamp | ✓ |
| processing_numbers| ✓ |
| agency            | ✓ |
| facility          | ✓ |
| charges           | ✓ |
| severity          | ✗ |
| bond_amount       | ✗ |
| current_status    | ✗ |
| court_dates       | ✗ |
| days_jailed       | ✓ |
| other\*           | ✓ |
| notes             | ✗ |

\*Other available data: charge count, bond type, disposition (e.g. 'Bonded Out', 'Dismissed'), height, weight, hair, eyes, charge warrant number, offense date, arrest date, arresting agency. These data can be added upon request.

inmate ID is Booking Number
results ordered by Booking Number
python webscraper.py (default) get 10 results from all = python webscraper.py all 0 10
python webscraper.py all 0 100000 (index number, number of results)
  num of results received may be less than input
python webscraper.py today
Discretion/Disclaimer: larger the sample size, longer the wait, will take few minutes

Need to work on severity

if you scrape too early, today will return nothing (what time should we scrape for today)

PROBLEM: Mosley, Devin Naeem

Num Results may be off a little due to not-working links

DAYS JAILED IS WRONG

REQUIREMENTS.TXT