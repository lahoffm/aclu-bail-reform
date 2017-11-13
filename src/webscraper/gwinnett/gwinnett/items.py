# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst
import datetime

DATE_OUTPUT_FORMAT = '%m/%d/%Y %H:%M:%S %Z'

BOOKING_DATE_INPUT_FORMAT = '%m/%d/%Y %H:%M:%S'


class GwinnettInmate(scrapy.Item):
    county_name = scrapy.Field()
    timestamp = scrapy.Field()
    url = scrapy.Field()
    inmate_id = scrapy.Field()
    inmate_lastname = scrapy.Field()
    inmate_firstname = scrapy.Field()
    inmate_middlename = scrapy.Field()
    inmate_sex = scrapy.Field()
    inmate_race = scrapy.Field()
    inmate_age = scrapy.Field()
    inmate_dob = scrapy.Field()
    inmate_address = scrapy.Field()
    booking_timestamp = scrapy.Field()
    release_timestamp = scrapy.Field()
    processing_numbers = scrapy.Field()
    agency = scrapy.Field()
    facility = scrapy.Field()
    charges = scrapy.Field()
    severity = scrapy.Field()
    bond_amount = scrapy.Field()
    current_status = scrapy.Field()
    court_dates = scrapy.Field()
    days_jailed = scrapy.Field()
    other = scrapy.Field()


def parse_race(race_val):
    if race_val == 'B':
        return GwinnettInmateLoader.Race.Black
    elif race_val == 'W':
        return GwinnettInmateLoader.Race.White
    else:
        return GwinnettInmateLoader.Race.Unknown

def parse_sex(sex_val):
    if sex_val == 'FEMALE':
        return GwinnettInmateLoader.Sex.Female
    elif sex_val == 'MALE':
        return GwinnettInmateLoader.Sex.Male
    else:
        return GwinnettInmateLoader.Sex.Unknown

def parse_severity(severity_val):
    if severity_val == 'F':
        return GwinnettInmateLoader.ChargeSeverity.Felony
    elif severity_val == 'M':
        return GwinnettInmateLoader.ChargeSeverity.Misdemeanor
    else:
        return GwinnettInmateLoader.ChargeSeverity.Unknown

def parse_timestamp(timestamp):
    return datetime.datetime.strptime(timestamp, BOOKING_DATE_INPUT_FORMAT)

def format_timestamp(timestamp):
    return timestamp.isoformat(' ')


class GwinnettInmateLoader(ItemLoader):

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

    class ChargeSeverity:
        Misdemeanor = 'misdemeanor'
        Felony = 'felony'
        Unknown = 'unknown'

    default_output_processor = TakeFirst()

    timestamp_out = MapCompose(format_timestamp)
    inmate_lastname_in = MapCompose(str.strip)
    inmate_firstname_in = MapCompose(str.strip)
    inmate_middlename_in = MapCompose(str.strip)
    inmate_sex_in = MapCompose(str.strip, parse_sex)
    inmate_race_in = MapCompose(str.strip, parse_race)
    inmate_age_in = MapCompose(str.strip, int)
    inmate_dob_in = MapCompose(str.strip)
    inmate_address_in = MapCompose(str.strip)
    booking_timestamp_in = MapCompose(str.strip, parse_timestamp)
    booking_timestamp_out = MapCompose(format_timestamp)
    release_timestamp_in = MapCompose(str.strip)
    processing_numbers_in = MapCompose(str.strip)
    agency_in = MapCompose(str.strip)
    facility_in = MapCompose(str.strip)
    charges_out = Join(' | ')
    severity_in = MapCompose(str.strip, parse_severity)
    severity_out = Join(' | ')
    bond_amount_in = MapCompose(str.strip)
    current_status_in = MapCompose(str.strip)
    court_dates_in = MapCompose(str.strip)
    days_jailed_in = MapCompose(str.strip)
    other_in = MapCompose(str.strip)
