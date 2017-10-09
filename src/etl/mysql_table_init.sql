# Populate the county table
USE jaildata;

/*# Only have to run once
INSERT INTO county (county_name) VALUES ('athens-clarke'),('bibb'),('chatham'),('cobb'),('columbia'),('dekalb'),('dougherty'),
                                         ('glynn'),('gwinnett'),('hall'),('henry'),('fulton'),('lowndes'),('muscogee'),
										('richmond'),('whitfield');
*/

UPDATE county SET homepage_url = 'https://www.athensclarkecounty.com/207/Jail-Section',
				  scrape_url = 'http://enigma.athensclarkecounty.com/photo/jailcurrent.asp',
                  phone = '706-613-3270',
                  email = 'sheriff@athensclarkecounty.com',
                  current_roster = 'yes',
                  booking_list = 'yes',
                  release_dates = 'yes',
                  race = 'yes',
                  notes = ''
			  WHERE county_name = 'athens-clarke';

SELECT * FROM county;