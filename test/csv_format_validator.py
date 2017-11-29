import os

directory = os.path.relpath('../data');
for root, dirs, files in os.walk(directory):
  for file in files:
    if file.endswith('.csv'):
      print(file);

      # for every file

        # county name (string, one of sixteen)

        # timestamp (YYYY-MM-DD hh:mm:ss EST)

        # url (https:// || http://)

        # inmate_id (string, number, both, none)

        # inmate_lastname (string or none)

        # inmate_firstname (string or none)

        # inmate_middlename (string or none)

        # inmate_sex (m, male, M, Male, MALE, f, female, F, Female, FEMALE)

        # inmate_race (string, race list)

        # inmate_age (number)

        # inmate_dob (YYYY-MM-DD)

        # inmate_address (string, address validator)

        # booking_timestamp (YYYY-MM-DD hh:mm:ss EST)

        # release_timestamp (YYYY-MM-DD hh:mm:ss EST)

        # processing_numbers (string, numbers, | , none)

        # agency (string, numbers)

        # facility (string, numbers)

        # charges (string, numbers, | , none)

        # severiy (m, misd, misdemanor, M, Misd, Misdemeanor, MISDEMEANOR, f, fel, felony, F, Fel, Felony, FELONY)

        # bond_amount (string, $float, | , none)

        # current_status (string, | , none)

        # court_dates (YYYY-MM-DD)

        # days_jailed (number)

        # other (anything)

        # notes (anything)

