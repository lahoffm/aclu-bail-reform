# Webscraper for Dekalb County Jail Records

This Python-based web scraper scrapes Dekalb County jail records from the [Dekalb County - Judicial Information System](https://ody.dekalbcountyga.gov/app/JailSearch/#/search) website.

The purpose of this project is to help build a case for the [ACLU Bail Reform Project](https://github.com/lahoffm/aclu-bail-reform#aclu-bail-reform-project) in the state of Georgia.

## Installation Requirements

- Python 3.6.3

```
pip install -r requirements.txt
```

Required packages are listed in *requirements.txt*.

## Commands & Usage

- The following commands create a CSV file (dekalb-\*.csv) in the *data* folder.
- Each row is a jail record. Jail records are sorted by inmate booking number.
- An inmate may have multiple records if there are multiple charges.
- Some records may be missing due to unknown circumstances. Jail IDs for missing records will be logged at the end of the scrape.

#### All Records
```
python webscraper.py all 0 100
```
Scrapes records starting from an index number for a certain number of records (e.g. `python webscraper.py all 12000 50` will search for 50 records starting from index 12000). An **index number** and **record size** must be specified as arguments.

**Note:** The larger the record size, the longer the runtime. For large record sizes, make sure network connection is stable for the entire duration of the scrape.

#### Today
```
python webscraper.py today
```
Scrapes all records, if any, for the current date. If this command is used before any inmate booking, it will respond with `No records found.`

#### Custom Date
```
python webscraper.py custom 1900-01-01
```
Scrapes all records for a custom date. A **custom date** (yyyy-mm-dd) must be specified as an argument. If there are no records for a specified date, it will respond with `No records found.`

#### Default
```
python webscraper.py
```
Scrapes records starting from index 0 for 100 records.

## Available Data
| Column Name                     | Data Available
|---------------------------------|---------------|
| county_name                     | ✓ |
| timestamp                       | ✓ |
| url                             | ✓ |
| inmate_id <sup>1</sup>          | ✓ |
| inmate_lastname                 | ✓ |
| inmate_firstname                | ✓ |
| inmate_middlename               | ✓ |
| inmate_sex                      | ✓ |
| inmate_race                     | ✓ |
| inmate_age                      | ✓ |
| inmate_dob                      | ✓ |
| inmate_address                  | ✓ |
| booking_timestamp               | ✓ |
| release_timestamp               | ✓ |
| processing_numbers <sup>2</sup> | ✓ |
| agency <sup>3</sup>             | ✓ |
| facility                        | ✓ |
| charges \*                      | ✓ |
| severity \*                     | ✓ |
| bond_amount \*                  | ✓ |
| current_status \*               | ✓ |
| court_dates                     | ✗ |
| days_jailed                     | ✓ |
| other <sup>4</sup>              | ✓ |
| notes                           | ✗ |

<sup>1</sup> Booking number.

<sup>2</sup> Contains SO#, booking number, jail ID, and arrest ID.

<sup>3</sup> Arresting agency.

<sup>4</sup> **Other available data**: charge count, charge warrant number, height, weight, hair, eyes, offense date, arrest date. These data can be added upon request.

\* *charges*, *severity*, *bond_amount* and *current_status* are parallel data. *bond_amount* contains bond type only. *current_status* is charge disposition. 

## Contributing
If you want to [contribute](https://github.com/lahoffm/aclu-bail-reform/blob/master/CONTRIBUTING.md) to the ACLU Bail Reform Project, contact [project owner](https://github.com/lahoffm/aclu-bail-reform).
