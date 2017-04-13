# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AirbnbItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    host_id = scrapy.Field()
    hosting_id = scrapy.Field()
    room_type = scrapy.Field()
    price = scrapy.Field()
    bed_type = scrapy.Field()
    person_capacity = scrapy.Field()
    nightly_price = scrapy.Field()
    listing_lat = scrapy.Field()
    listing_lng = scrapy.Field()
    url = scrapy.Field()



