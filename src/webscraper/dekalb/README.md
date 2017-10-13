# POST Request for Dekalb county
* Python 3.6.3
* Retrieves records for [Dekalb county jail](https://ody.dekalbcountyga.gov/app/JailSearch/#/search)

# How to run
* Run ```python search_req.py```
* Makes 1 CSV file (dekalb.csv)

| Column Name       | Data Available
|-------------------|---------------|
| county_name       | ✓ |
| timestamp         | ✗ |
| url               | ✓ |
| inmate_id         | ✗ |
| inmate_lastname   | ✓ |
| inmate_firstname  | ✓ |
| inmate_middlename | ✓ |
| inmate_sex        | ✗ |
| inmate_race       | ✗ |
| inmate_age        | ✓ |
| inmate_dob        | ✓ |
| inmate_address    | ✗ |
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
| days_jailed       | ✗ |
| other\*           | ✓ |
| notes             | ✗ |

\*inmate_type, arrest_id, arresting_agency, jail_id, charge_count, so#

