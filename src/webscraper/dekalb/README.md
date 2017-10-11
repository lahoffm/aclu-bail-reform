# POST Request for Dekalb county
* Python 3.6.3
* Retrieves records for [Dekalb county jail](https://ody.dekalbcountyga.gov/app/JailSearch/#/search)

# How to run
* Run ```python search_req.py```
* Makes 1 CSV file (dekalb.csv)

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
| other             | \*|
| notes             | ✗ |

\*Other available data: charge count, bond type, disposition (e.g. 'Bonded Out', 'Dismissed'), height, weight, hair, eyes, charge warrant number, offense date, arrest date, arresting agency.

inmate ID is Booking Number
results ordered by Booking Number
python webscraper.py (default) get 10 results from all = python webscraper.py all 0 10
python webscraper.py all 0 100000 (index number, number of results)
  num of results received may be less than input
python webscraper.py today
Discretion: larger the sample size, longer the wait, will take few minutes

Need to work on severity

if you scrape too early, today will return nothing (what time should we scrape for today)