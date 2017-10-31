# -*- coding: utf-8 -*-
import scrapy
import csv
import re
import pandas as pd
from warnings import warn
from datetime import datetime

class BibbSpider(scrapy.Spider):
    name = 'bibb'
    allowed_domains = ['co.bibb.ga.us']
    start_urls = ['http://www.co.bibb.ga.us/BSOInmatesOnline/CurrentDayMaster.asp']
    custom_settings = {
        'FEED_URI': '../../../../data/bibb_%s.csv' % datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
        'FEED_FORMAT': 'csv'
    }

    def closed(self, reason):
        """ After spider finishes, erases blank lines in CSV. """
        csv_fname = self.custom_settings['FEED_URI']
        print('Erasing blank lines in ' + csv_fname)
        with open(csv_fname, newline='') as f:
           rows = list(csv.reader(f))
        rows = rows[0::2] # erase blank lines
        with open(csv_fname, 'w', newline='') as f:
            writer = csv.writer(f, lineterminator='\n')
            for row in rows:
                writer.writerow(row)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'bib-%s.html' % page

        for href in response.css('table tr > td > a::attr(href)'):
            yield response.follow(href, callback=self.parseRecord)

    def parseRecord(self, response):
        fontTag = False
        
        def formatXpathSelector(xpathSelector):
            if fontTag:
                return record.xpath("translate(normalize-space(\
                    %s/td[2]/strong/font/text()), ' ', '')" % xpathSelector)
            else:
                 return record.xpath("translate(normalize-space(\
                    %s/td[2]/strong/text()), ' ', '')" % xpathSelector)                   

        def extract(xpathSelector):
            return formatXpathSelector(xpathSelector).extract_first()

        def extractExact(xpathSelector):
            return record.xpath(xpathSelector).extract_first()

        def extractAll(xpathSelector):
            return record.xpath(xpathSelector).extract()

        def formatInmateName(initialName):
            lastName = initialName.pop(0)
            # Remove comma
            initialName.pop(0)
            firstName = initialName.pop(1)
            middleName = ''.join(initialName).strip()
            return {
                'first': firstName,
                'middle': middleName,
                'last': lastName
            }

        def parseRaceSex(input):
            value = input.split('/')
            race = value[0].strip()
            notes = ''
            if race=='B':
                race = 'black'
            elif race=='W':
                race = 'white'
            else:
                notes = 'Unknown race "' + race + '", left race blank'
                race = ''
            return {
                'race': race,
                'sex': value[1].strip().lower(),
                'notes': notes
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
                
                # If inmate is 'Released' there's an additional font color tag
                # "other" says if inmate currently in jail or released
                fontTag = False 
                other = extract('./tr[10]')
                if other == 'InJail':
                    other = 'In Jail';
                else:
                    fontTag = True
                    other = extract('./tr[10]')
                fontTag = False
                
                # Extract charges & current status of each charge
                charges_table = extractAll('./tr[13]//table')
                charges_df = pd.read_html(charges_table[0], header=None, converters={0:str, 1:str})[0]
                charges_df.fillna('', inplace=True)
                charges = charges_df.iloc[:, 0].str.cat(sep=' | ')
                currentStatus = charges_df.iloc[:, 1].str.cat(sep=' | ') # like "Bond posted"
                
                # Extract charge severity
                charges_df['severity'] = ''
                felony_mask = charges_df.iloc[:, 0].str.lower().str.contains('felony')
                misdemeanor_mask = charges_df.iloc[:, 0].str.lower().str.contains('misdemeanor')
                charges_df.loc[felony_mask, 'severity'] = 'felony'
                charges_df.loc[misdemeanor_mask, 'severity'] = 'misdemeanor' 
                severity = charges_df['severity'].str.cat(sep=' | ')

                # Extract bond amount
                bondAmount = extract('./tr[11]').replace(u'\xa0',u'')
                bondAmount = bondAmount.replace(',','')
                bondAmount = bondAmount.replace(' ','')
                if bondAmount=='$':
                    bondAmount = ''
                
                # Extract booking timestamp
                timestamp_fmt = '%Y-%m-%d %H:%M:%S EST'
                bookingTimestamp = extract('./tr[8]').replace(u'\xa0',u'').replace(' ','')
                try:
                    bookingTimestamp = datetime.strptime(bookingTimestamp,'%m-%d-%Y/%H:%M:%S').strftime(timestamp_fmt)
                except ValueError as e:
                    bookingTimestamp = datetime.strptime(bookingTimestamp, '%m-%d-%Y/').strftime('%Y-%m-%d')
                
                # Extract release timestamp
                releaseTimestamp = extract('./tr[12]').replace(u'\xa0',u'').replace(' ','')
                if releaseTimestamp == '/':
                    releaseTimestamp = ''
                else:
                    releaseTimestamp = datetime.strptime(releaseTimestamp,'%m-%d-%Y/%H:%M:%S').strftime(timestamp_fmt)

                yield {
                    'county_name': 'bibb',
                    'timestamp': datetime.now().strftime(timestamp_fmt),
                    'url': response.url,
                    'inmate_id': inmateId.replace(u'\xa0',u''),
                    'inmate_lastname': inmateName['last'].replace(u'\xa0',u''),
                    'inmate_firstname': inmateName['first'].replace(u'\xa0',u''),
                    'inmate_middlename': inmateName['middle'].replace(u'\xa0',u''),
                    'inmate_sex': raceSex['sex'],
                    'inmate_race': raceSex['race'],
                    'inmate_age': calculateAge(yearOfBirth),
                    'inmate_dob': yearOfBirth,
                    'inmate_address': inmateAddress.replace(u'\xa0',u''),
                    'booking_timestamp': bookingTimestamp,
                    'release_timestamp': releaseTimestamp,
                    'processing_numbers': '',
                    'agency': extract('./tr[9]').replace(u'\xa0',u''),
                    'facility': '',
                    'charges': charges.replace(u'\xa0',u''),
                    'severity': severity,
                    'bond_amount': bondAmount,
                    'current_status': currentStatus.replace(u'\xa0',u''),
                    'court_dates': '',
                    'days_jailed': '',
                    'other': other,
                    'notes': raceSex['notes']
                }
