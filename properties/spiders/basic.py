# -*- coding: utf-8 -*-
import scrapy
import urlparse
import socket
import datetime
from properties.items import PropertiesItem
from scrapy.loader.processors import MapCompose, Join
from scrapy.loader import ItemLoader

class BasicSpider(scrapy.Spider):
    name = "basic"
    allowed_domains = ["gumtree.com"]
    start_urls = (
            'https://www.gumtree.com/p/property-for-sale/4-5-bedroom-house-for-sale-in-ardersier-/1280668353',
    )

    def parse(self, response):
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