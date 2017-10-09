# Current priorities & timeline

We are using **Python 3.6**.  

* Priority #1 is writing webscrapers for each county, so we can collect daily jail data.
* **Current goal:** start daily data collection for 4 or more counties by November 1.
* County jail info [here](https://github.com/lahoffm/aclu-bail-reform/blob/master/docs/County-jail-summaries.xlsx)
* [Pick an unclaimed county](https://github.com/lahoffm/aclu-bail-reform/issues) and start scraping!
* Once we have data we can work on ETL/visualization
* ACLU will lobby at next GA state legislative session starting Jan 2018. Ideally we'll have some visualizations by then. But their bail reform project will be ongoing beyond then.  


# CSV file format for webscrapers **(TENTATIVE - I welcome suggestions. Please submit pull request with your changes to this format)**

* Each webscraper should output a CSV file into [```data``` folder](https://github.com/lahoffm/aclu-bail-reform/tree/master/data)
* **CSV name**: ```lowercase-county-name_optional-extra-identifier_yyyy_mm_dd_hh_mm_ss.csv```. The extra identifier is if it's better to make >1 CSV per scrape. For example, if the jail has separate "last 14 day arrests" and "last 14 day releases" it's better to put in 2 CSVs and let ETL code handle that.
* Use [```csv.writer```](https://docs.python.org/3/library/csv.html#csv.writer) with the [default parameters](https://docs.python.org/3/library/csv.html#csv-fmt-params) so all scrapers handle commas within fields the same way. Line terminator doesn't matter (```\r```, ```\n``` or ```\r\n```)
* <a name="semicolon_behavior">Semicolons</a> ```';'``` are separators within a field, like if an inmate has multiple charges.
	* **To prevent a bug**, webscraper should replace text field ```';'``` with ```':'```.
	* If a field is supposed to match another field (i.e. ```severity='misdemeanor;misdemeanor;felony'``` matching ```charges='charge1;charge2;charge3'```), but data is missing, make empty strings so ETL parser knows how to pair things up. Example for 3 values:
		* 1st value missing, do: ```;misdemeanor;felony```
		* 2nd value missing, do: ```misdemeanor;;felony```
		* 3rd value missing, do: ```misdemeanor;misdemeanor;```
		* All values missing, do: ```;;```
* One column header row, then one row per inmate. Include **all** inmates available when the site was scraped. Even if the same inmates were there yesterday - we'll handle that later.
* Uppercase/lowercase is irrelevant, ETL code will probably lowercase everything.
* We prefer as many columns scraped as possible. Who knows what :gem::gem::gem: we could mine? But if pressed for time, scrape the columns critical to [project goals](https://github.com/lahoffm/aclu-bail-reform/raw/master/docs/ACLU-Bail-Reform-One-pager.pdf).

# CSV columns, in order
*If your county doesn't provide the data, leave the column blank.*  

Column name | Column description
------------ | -------------
county_name | County name like ```'athens-clarke'```, ```'bibb'```
timestamp | [Postgres timestamp format](https://www.postgresql.org/docs/9.1/static/datatype-datetime.html): ```'2004-10-19 10:23:54 EST'``` - when row was scraped. Can have same stamp for all the rows if more convenient.
url | URL the row was scraped from
inmate_id | Inmate ID number if county posts it. Maybe useful later to look up inmates' eventual outcome.
inmate_lastname | Last name
inmate_firstname | First name
inmate_middlename | Middle name or initial, if any
inmate_sex	| ```'m'/'f'```
inmate_race	| ```'black'/'white'/'hispanic'/'asian'/'middle-eastern'/'native-american'/'pacific-islander'```. Although someone's race/ethnicity is more complicated (and really shouldn't matter anyway) we will stick to the basic categories the counties designated. If you see a category not on this list, please inform us so we can add to the list.
inmate_age | Age in years. If ```inmate_dob``` only provides the year, just subtract birth year from current year.
inmate_dob	| Date of birth, [Postgres timestamp format](https://www.postgresql.org/docs/9.1/static/datatype-datetime.html), ```'2004-10-19'```. Some counties only post year of birth.
inmate_address | Address, including if they list no address. Useful later to see where arrests are clustering. Just insert how the county lists it, ETL code can parse it into standard format later.
booking_timestamp | [Postgres timestamp format](https://www.postgresql.org/docs/9.1/static/datatype-datetime.html), ```'2004-10-19 10:23:54 EST'``` - if county doesn't post time, just insert date. If they just post arrest time, insert that, because booking would occur soon after that.
release_timestamp | [Postgres timestamp format](https://www.postgresql.org/docs/9.1/static/datatype-datetime.html), ```'2004-10-19 10:23:54 EST'``` - only fill out if they list an inmate as released. If county doesn't post time, just insert date. This data could be in separate release records or listed side-by-side with the booking/roster/inmate-name records. ETL code will decide for each county how to interpret absence of release date. If release date is posted as ```Estimated```, append to timestamp like ```'2004-10-19 10:23:54 EST estimated'```. If inmate has multiple releases listed (one for each charge), separate with semicolons in same order as the ```charges```.  See [Note](#semicolon_behavior)
processing_numbers | Arrest/booking/case/docket IDs if county posts them. Prefix with brief description like ```'Police case #12345'``` or ```'Docket ID for charge 3: 12345'```. If multiple IDs available, separate with semicolons like with ```charge```. Maybe useful later to look up inmates' eventual outcome.
agency | Arresting/booking agency, only if specifically listed. Could be useful to target policy advocacy if county has multiple agencies
facility | Facility at which inmate is held. Leave blank if they don't post it, maybe county only has one jail. Could be useful for determining specific jails of interest.
charges	| Charges, same text as on website. ETL code can reconcile the county-specific formats that refer to the same charge. If multiple charges are listed, separate them with semicolons like ```'marijuana poss.;resisting arrest;driving under inf'```. If the charge refers to a legal code, list the code first, before the charge's descriptive text, like ```'OCGA16-13-30(a) Poss of Meth'```
severity | ```'misdemeanor'/'felony'``` - if not available, ETL code can determine this. If multiple charges, separate with semicolons like ```'misdemeanor;misdemeanor;felony'``` - in the same order as the charges. See [Note](#semicolon_behavior)
bond_amount | Bond/bail amount in dollars, followed by space, then any other bond-related text, - like ```'$1000.00 state bond, type = surety, cleared'```. ```$``` prefix tells ETL code it's a number. Alternatively, if there was no bond set (such as a violent offender) just insert what it says like ```'held without bond'```. If different bonds listed for each charge, separate with semicolons in the same order as the ```charges```. See [Note](#semicolon_behavior)
current_status | Current status for each charge. For example, Columbia county posts ```AWAITING TRIAL/SENTENCED``` and some counties post disposition such as ```time served```. If multiple charges, separate with semicolons in the same order as the charges, like ```'awaiting trial;time served;unknown status'``` See [Note](#semicolon_behavior)
court_dates | Next court dates, [Postgres timestamp format](https://www.postgresql.org/docs/9.1/static/datatype-datetime.html), ```'2004-10-19'```. If multiple dates, separate with semicolons and add descriptive text like ```'2004-10-19, charge 1;2004-10-22, charge 2'```. Eventually this can help determine how long someone sat in jail before court appearance, if roster data shows they were never released on bail. See [Note](#semicolon_behavior)
days_jailed | Days in custody as of ```timestamp```. Some counties explicitly post this. Otherwise, keep blank and let ETL code try to infer it from other information.
other | Any other data you feel is potentially useful. Please let us know, maybe we'll add it to the CSV format in the future.
notes | Auto-generated notes & error messages separated by semicolons. Use it to log unusual things about the row's data, like ```Inmate race not listed;Could not access inmate detail page, http error 404```