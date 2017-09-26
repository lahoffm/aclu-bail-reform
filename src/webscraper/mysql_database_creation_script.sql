# Creates empty database for dumping raw html from jail websites.
# Can be run from MySQL Workbench or copy-pasted into sqlalchemy statements.
CREATE DATABASE IF NOT EXISTS jaildata;
USE jaildata;

CREATE TABLE county (
	county_name		VARCHAR(255)	PRIMARY KEY, # county name
    homepage_url	VARCHAR(255)	UNIQUE, # homepage of county jail
	scrape_url		VARCHAR(255)	UNIQUE, # entry URL for webscraping jail data
    phone			VARCHAR(255)	UNIQUE, # jail contact phone #
    email			VARCHAR(255)	UNIQUE, # jail contact email
    current_roster	ENUM('yes','no'), # yes if jail provides complete roster of current inmates
    booking_list	ENUM('yes','no'), # yes if jail provides list of all recent bookings, no if only allows inmate name search
    release_dates	ENUM('yes','no'), # yes if jail provides release dates
    notes			VARCHAR(255)	  # user-friendly notes about each county
) ENGINE = InnoDB;

CREATE TABLE scrape_records (
	scrape_id	INT				PRIMARY KEY		AUTO_INCREMENT,		# every time one county jail is scraped
    county_name	VARCHAR(255)	NOT NULL,
	time_stamp	DATETIME		NOT NULL,	# time raw data was dumped to this db. Dump function should run right after getting the last html page
	notes		VARCHAR(255),	# user-friendly notes about a particular scrape record
    CONSTRAINT fk_county FOREIGN KEY (county_name) REFERENCES county (county_name)
) ENGINE = InnoDB;

CREATE TABLE raw_data (
	scrape_id		INT					NOT NULL, # one scrape can have multiple html pages
    html_id			INT					NOT NULL, 	# 1, 2, 3, ... for each html page scraped on a given day for a given county jail
	single_inmate	ENUM('yes','no'), # yes if it's a subpage showing details for a single inmate. no if it lists multiple inmates.
    url				VARCHAR(255)		NOT NULL,  # URL of single webpage of scraped data
    entry_url		VARCHAR(255), # if it's a single-inmate subpage, where did we click the link to get that subpage? Can be NULL if N/A.
    headers			TEXT,	 # http response headers up to 65 KB
    rawdata			MEDIUMTEXT, # Raw HTML/javascript source from single webpage up to 16 MB
    notes			VARCHAR(255), # user-friendly notes about a particular webpage
    CONSTRAINT html_unique_id PRIMARY KEY (scrape_id, html_id),
    CONSTRAINT fk_scrape_records FOREIGN KEY (scrape_id) REFERENCES scrape_records (scrape_id)
) ENGINE = InnoDB;
