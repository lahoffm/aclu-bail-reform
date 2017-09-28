# -*- coding: utf-8 -*-
import scrapy
import csv
import re
from datetime import datetime

class BibbSpider(scrapy.Spider):
    name = 'bibb'
    allowed_domains = ['co.bibb.ga.us']
    start_urls = ['http://www.co.bibb.ga.us/BSOInmatesOnline/CurrentDayMaster.asp']
    custom_settings = {
        'FEED_URI': 'output/bibb-output-%s.csv' % datetime.now(),
        'FEED_FORMAT': 'csv'
    }

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'bib-%s.html' % page

        for href in response.css('table tr > td > a::attr(href)'):
            yield response.follow(href, callback=self.parseRecord)

    def parseRecord(self, response):

        def formatXpathSelector(xpathSelector):
            return record.xpath("translate(normalize-space(\
                %s/td[2]/strong/text()), ' ', '')" % xpathSelector)

        def extract(xpathSelector):
            return formatXpathSelector(xpathSelector).extract_first()

        def extractExact(xpathSelector):
            return record.xpath(xpathSelector).extract_first()

        def formatInmateName(initalName):
            lastName = initalName.pop(0)
            # Remove comma
            initalName.pop(0)
            firstName = initalName.pop(1)
            middleName = ''.join(initalName).strip()
            return {
                'first': firstName,
                'middle': middleName,
                'last': lastName
            }

        def parseRaceSex(input):
            value = input.split('/')
            return {
                'race': value[0].strip(),
                'sex': value[1].strip()
            }

        def parseAddress(input):
            splitNewLines = input.split('<br>')
            joinAddress = splitNewLines[1] + splitNewLines[2]
            strippedAddress = joinAddress.replace('</strong>', '').strip()
            return ' '.join(strippedAddress.split())

        def calculateAge(yearOfBirth):
            currentYear = datetime.now().year
            return int(currentYear) - int(yearOfBirth)

        for record in response.css('table'):
            inmateId = extract('./tr[2]')
            if (inmateId):
                inmateName = formatInmateName(
                    re.findall(r'\s|,|[^,\s]+', extract('./tr[3]'))
                )
                raceSex = parseRaceSex(extract('./tr[4]'))
                inmateAddress = parseAddress(
                    extractExact('./tr[3]/td[2]/strong')
                )
                yearOfBirth = extract('./tr[5]')

                yield {
                    'county_name': 'bibb',
                    'timestamp': datetime.now(),
                    'url': response.url,
                    'inmate_id': inmateId,
                    'inmate_lastname': inmateName['last'],
                    'inmate_firstname': inmateName['first'],
                    'inmate_middlename': inmateName['middle'],
                    'inmate_sex': raceSex['sex'],
                    'inmate_race': raceSex['race'],
                    'inmate_age': calculateAge(yearOfBirth),
                    'inmate_dob': yearOfBirth,
                    'inmate_address': inmateAddress,
                    'booking_timestamp': extract('./tr[8]'),
                    'release_timestamp': extract('./tr[12]'),
                    'processing_numbers': '',
                    'agency': extract('./tr[9]'),
                    'facility': '',
                    'charges': extractExact('./tr[13]//table/tr/td[1]/strong/text()'),
                    'severity': '',
                    'bond_amount': extract('./tr[11]'),
                    'current_status': extract('./tr[10]'),
                    'court_dates': '',
                    'days_jailed': '',
                    'other': ''
                }
