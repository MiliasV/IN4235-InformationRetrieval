# -*- coding: utf-8 -*-
import json
import logging
import scrapy

from airbnb.items import AirbnbItem

QUERY = 'http://airbnb.com/s/Amsterdam--Netherlands?price_min='

class BnbspiderSpider(scrapy.Spider):
    name = "bnbspider"
    allowed_domains = ["airbnb.com"]

    # this method creates the URLs that the Spider will begin to crawl based on
    # a range of prices because Airbnb returns only 300 results per search
    # returns an iterable of Requests
    def start_requests(self):
        urls = []
        range = 3
        i = 10
        while i <= 400:
            urls.append(QUERY + str(i) + '&price_max=' + str(i+range))
            i += range
            # increase the range as there are not many accomodations when the prices are that high
            if i > 280:
                range = 55
        urls.append(QUERY+str(400))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # this method is called by default to handle the response downloaded for each of the requests made
    def parse(self, response):
        # get the last page number on the page
        last_page_number = self.last_pagenumber_in_search(response)
        if last_page_number < 1:
            # abort the search if there are no results
            return
        else:
            # loop over all pages and scrape
            page_urls = [response.url + "&page=" + str(pageNumber)
                         for pageNumber in range(1, last_page_number + 1)]
            for page_url in page_urls:
                yield scrapy.Request(page_url,
                                     callback=self.parse_listing_results_page)

    # get the last page number
    def last_pagenumber_in_search(self, response):
        try:
            last_page_number = int(response
                                   .xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href')
                                   .extract()[0]
                                   .split('page=')[1]
                                   )
            return last_page_number

        except IndexError:  # if there is no page number
            # get the reason from the page
            reason = response.xpath('//p[@class="text-lead"]/text()').extract()
            # and if it contains the key words set last page equal to 0
            if reason and ('find any results that matched your criteria' in reason[0]):
                logging.log(logging.DEBUG, 'No results on page' + response.url)
                return 0
            else:
            # otherwise we can conclude that the page
            # has results but that there is only one page.
                return 1

    # parse the results from each page by extracting the href inside the image
    # and pass the response to the final request
    def parse_listing_results_page(self, response):
        for href in response.xpath('//a[@class="mediaPhoto_1bow0j6-o_O-mediaCover_n02jag"]/@href').extract():
            # get all href of the speficied kind and join them to be a valid url
            url = response.urljoin(href)
            # request the url and pass the response to final listings parsing function
            yield scrapy.Request(url, callback=self.parse_listing_contents)

    # parse the final attributes that we want by extracting the metadata with the specific id
    def parse_listing_contents(self, response):
        item = AirbnbItem()

        json_array = response.xpath('//meta[@id="_bootstrap-room_options"]/@content').extract()

        if json_array:
            airbnb_json_all = json.loads(json_array[0])


            airbnb_json = airbnb_json_all['airEventData']


            item['host_id'] = airbnb_json_all['hostId']
            item['hosting_id'] = airbnb_json['hosting_id']
            item['room_type'] = airbnb_json['room_type']
            item['price'] = airbnb_json['price']
            item['bed_type'] = airbnb_json['bed_type']
            item['person_capacity'] = airbnb_json['person_capacity']
            item['listing_lat'] = airbnb_json['listing_lat']
            item['listing_lng'] = airbnb_json['listing_lng']
            item['nightly_price'] = airbnb_json_all['nightly_price']
        item['url'] = response.url
        yield item



