class GwinnettInmateRecord:
    class Race:
        Asian = 'asian'
        Black = 'black'
        Hispanic = 'hispanic'
        Middle_Eastern = 'middle-eastern'
        Native_American = 'native-american'
        Pacific_Islander = 'pacific-islander'
        Unknown = 'unknown'
        White = 'white'

    class Sex:
        Female = 'f'
        Male = 'm'
        Unknown = 'unknown'

    def __init__(self, scrape_time):
        self.county_name = "gwinnett"
        self.timestamp = scrape_time
        self.url = "http://www.gwinnettcountysheriff.com/smartwebclient/"


    def get_field_names_csv(self):
        return [
            'county_name',
            'timestamp',
            'url',
            'inmate_id',
            'inmate_lastname',
            'inmate_firstname',
            'inmate_middlename',
            'inmate_sex',
            'inmate_race',
            'inmate_age',
            'inmate_dob',
            'inmate_address',
            'booking_timestamp',
            'release_timestamp',
            'processing_numbers',
            'agency',
            'facility',
            'charges',
            'severity',
            'bond_amount',
            'current_status',
            'court_dates',
            'days_jailed',
            'other'
        ]

    def get_field_values_csv(self):
        return [
            self.county_name,
            self.timestamp,
            self.url,
            self.id,
            self.lastname,
            self.firstname,
            self.middlename,
            self.sex,
            self.race,
            self.age,
            self.dob,
            self.address,
            self.booking_timestamp,
            self.release_timestamp,
            self.processing_numbers,
            self.agency,
            self.facility,
            self.charges,
            self.severity,
            self.bond_amount,
            self.current_status,
            self.court_dates,
            self.days_jailed,
            self.other
        ]