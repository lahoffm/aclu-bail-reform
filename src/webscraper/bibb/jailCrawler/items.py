# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JailcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    jacketId = scrapy.Field()
    race = scrapy.Field()
    sex = scrapy.Field()
    dob = scrapy.Field()
    status = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)
