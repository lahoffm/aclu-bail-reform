# -*- coding: utf-8 -*-
import scrapy
import csv
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

        for record in response.css('table'):
            jacketId = extract('./tr[2]')
            if (jacketId):
                yield {
                    'jacketId': jacketId,
                    'name': extract('./tr[3]'),
                    'race/sex': extract('./tr[4]'),
                    'dob': extract('./tr[5]'),
                    'timeOfArrest': extract('./tr[8]'),
                    'arrestAgency': extract('./tr[9]'),
                    'currentStatus': extract('./tr[10]'),
                    'bondAmount': extract('./tr[11]'),
                    'timeReleased': extract('./tr[12]'),
                    'charge': extractExact('./tr[13]//table/tr/td[1]/strong/text()'),
                    'dateUpdated': datetime.now()
                }
