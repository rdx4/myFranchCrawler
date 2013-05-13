# -*- coding: utf-8 -*-
'''
Created on apr 25, 2013
DONE
@author: Tzachi
'''


import re
from urlparse import urljoin
from bs4 import BeautifulSoup as bs
#import BeautifulSoup as bs
import time
from estater.crawler.crawler_base import CrawlerBase
from estater.crawler.utils import to_int


MAX_PAGES = 300


class MyFrenchHouse(CrawlerBase):
    '''
    my-french-house.com crawler
    '''
    def do_get_root_url(self):
        return r'http://www.my-french-house.com'

    def do_crawl(self):
        
        
        query_tpl = 'http://www.my-french-house.com/property-for-sale-france/search&order=date+desc&exact-property_status=-Sold&num=10&property_type=&property_price-from=0&property_price-to=&start=0/ee.php/property-for-sale-france/search&order=date+desc&exact-property_status=-Sold&num=10&property_type=&property_price-from=0&property_price-to=&start=0/P{prop_index}/'
        for i in xrange(MAX_PAGES):
            
            query = query_tpl.format(prop_index=i * 10)
            page = self.get_page(query)
            soup = bs(page)
            uls = soup.find_all('ul', {'class' :'results-header'})
            divs = soup.find_all('div', {'class' :'resultsDetail'})
            if len(divs) < 3:
                break
            for div in divs:
                e = self._parse_estate(div , uls , query)
                if e: 
                    print e
                    yield(e)
                    

    def _parse_estate(self, div ,uls , url):
        #get link
        link = urljoin(url, div.h3.a['href'])
       
        ps = div.find_all('p')
        # first paragraph  -- contain price
        bPrice = ps[0].b.text.strip()
        m = re.search(ur'€\b([\d,]+)', bPrice, re.I)
        if m:
            price = to_int(m.group(1))
        
        
        # second paragraph  -- contain city and bedrooms
        p2text = ps[1].text.strip()
        print p2text
        #get city
        m = re.search(r'(\w+),', p2text , re.I)
        if not m:
            return None
        city = m.group(1)

           
        # get rooms
        rooms = None
        m = re.search(r'Bedrooms: (\d+)', p2text, re.I)
        if m:
            rooms = to_int(m.group(1))
       
        
        # third  paragraph  -- contain description
        desc = ps[2].text.strip()
        
        #get picture (small)
        image = urljoin(url, div.a.img['src'])

        return self.create_estate(link, 'FR', 'EUR', city=city, price=price, rooms=rooms, description=desc , image = image)


def crawl(max_items, max_time):
    return MyFrenchHouse().crawl(max_items, max_time)
