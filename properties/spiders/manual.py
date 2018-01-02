# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
import socket
import datetime
from scrapy.http import Request
from properties.items import PropertiesItem
from scrapy.loader.processors import MapCompose, Join
from scrapy.loader import ItemLoader

class BasicSpider(scrapy.Spider):
    name = "manual"
    allowed_domains = ["gumtree.com"]
    start_urls = (
            'https://www.gumtree.com/flats-houses',
    )

    def parse(self, response):
        # Get the next index URLs and yield Requests
        next_selector = response.xpath('//*[@class="pagination-next"]/a/@href')
        for url in next_selector.extract():
            item_selector = response.xpath('//a[@class="listing-link"]/@href')
            for url in item_selector.extract():
                yield Request(urlparse.urljoin(response.url, url), callback=self.parse_item)
            
    # Xpath for Next: //*[@class="pagination-next"]/a/@href
    # Xpath for items: //a[@class="listing-link"]/@href

    def parse_item(self, response):
        l = ItemLoader(item=PropertiesItem(), response=response)
        
        l.add_xpath('title', '//h1[@id="ad-title"]/text()', MapCompose(unicode.strip, unicode.title))
        l.add_xpath('price', '//strong[contains(@class, "ad-price")]/text()', MapCompose(lambda i: i.replace(',', ''), float), re='[,.0-9]+')
        l.add_xpath('description', '//p[@class="ad-description"][1]/text()', MapCompose(unicode.strip), Join())
        l.add_xpath('address', '//span[@itemprop="address"]/text()', MapCompose(unicode.strip))
        l.add_xpath('image_urls', '/descendant::img[@itemprop="image"][1]/@src', MapCompose(lambda i: urlparse.urljoin(response.url, i)))
        
        l.add_value('url', response.url)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        l.add_value('date', datetime.datetime.now())

        return l.load_item()
    
#        item = PropertiesItem()
#        item['title'] =  response.xpath('//h1[@id="ad-title"]/text()').extract()
#        item['price'] = response.xpath('//strong[contains(@class, "ad-price")]/text()').extract()[0].strip()
#        item['description'] = response.xpath('//p[@class="ad-description"][1]/text()').extract()
#        item['address'] = response.xpath('//span[@itemprop="address"]/text()').extract()
#        item['image_urls'] = response.xpath('/descendant::img[@itemprop="image"][1]/@src').extract()
#        return item