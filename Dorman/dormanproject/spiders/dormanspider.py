
# -*- coding: utf-8 -*-
import scrapy
import json
import re
import logging
from scrapy import signals
from scrapy import Spider
from urllib.parse import urljoin
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from string import whitespace
import os
import time

class DormanSpider(scrapy.Spider):
    name = 'dormanspider'
    allowed_domains = ['dormanproducts.com']
    handle_httpstatus_list = [301, 302]
    url_templates = 'https://www.dormanproducts.com/gsearch.aspx?type=oesearch&origin=oesearch&q={}'

    def __init__(self, *args, **kwargs):
        self.args = str(args)
        self.index = [x.strip("([])").lower() for x in self.args.split(',')]
        #self.str1= self.args.strip("([])")
        #self.index=self.str1.strip("''")
        super(DormanSpider,self).__init__(*args, **kwargs)


    def start_requests(self):
        for code in self.index:
            #code = self.index.strip(whitespace + "'],")
            code=code.strip(whitespace + "'")
            if code:
                url = self.url_templates.format(code)
                yield scrapy.Request(url, callback=self.parse_listing,meta={'part_no':code})


    def parse_listing(self, response):
        logging.info('Parsing listings...{}'.format(response.url))
        
        sel = Selector(response)
        links = sel.xpath('//div[@class="row searchResults"]').extract()
        for i in links:
            parse = Selector(text=i)
            itemname = parse.xpath('//span[@class="item-name"]/text()').get()
            iteminfo = parse.xpath('//h4/text()').get()
            itemsum = parse.xpath('string(//p)').get()
            tabledet1=parse.xpath('//table//thead//tr').extract()
            headlist=[]
            for i in tabledet1:
                parse3=Selector(text=i)
                tablehead = parse3.xpath('//th/text()').get()
                headlist.append(tablehead)
            headtup=tuple(headlist)
            joinstr1="".join(headtup)
            tablebod1=parse.xpath('//table//tbody//tr').extract()
            bodylist1,bodylist2=[],[]
            for i in tablebod1:
                parse4=Selector(text=i)
                tablebody = parse4.xpath('//th/text()').get()
                tabledata = parse4.xpath('//td/text()').get()
                bodylist1.append(tablebody)
                bodylist2.append(tabledata)
            bodyref=tuple(bodylist1)
            bodymfr=tuple(bodylist2)
            oeref="".join(bodyref)
            mfrname="".join(bodymfr)
            product_details = {
                'partno':response.meta['part_no'],
                'ProductName': itemname,
                'ProductInfo': iteminfo,
                'ProductSummary': itemsum,
                'Cross': joinstr1,
                'OEref': oeref,
                'MfrName': mfrname
                }
            next_page = parse.xpath('//a[@class="btn btn-darkgrey centered detail-btn"]/@href').extract_first()
            if next_page:
                url = urljoin('https://www.dormanproducts.com/', next_page)
                yield scrapy.Request(url, callback=self.detailparse, meta={'details': product_details,'dont_merge_cookies': True, 'dont_filter': True})
        #sub_page = sel.xpath('//a[text()="2"]/@href').extract_first()
        #logging.info('sub page is {}'.format(sub_page))
        #if sub_page:
         #   sub_page = urljoin(response.url, sub_page).split('?')[0].strip()
          #  logging.info('next page value is....{}'.format(sub_page))
           # yield scrapy.Request(sub_page, callback=self.parse_listing)


    def detailparse(self, response):
        sel = Selector(response)
        tabledetails = sel.xpath('//section[@id="productOE"]').extract_first()
        if tabledetails:
            oe_details=[]
            parse1 = Selector(text=tabledetails)
            tbodyval=parse1.xpath('//table//tbody//tr').extract()
            for i in tbodyval:
                parse2 = Selector(text=i)
                oehead = parse2.xpath('//th//text()').get()
                oedata = parse2.xpath('//td//text()').get()
                oelist=(oehead +':'+ oedata)
                oe_details.append(oelist)
            oetup=tuple(oe_details)
            joined_string = "".join(oetup)
            oe_det = {
                    'Oedetails': joined_string
                    }
            finalresult = response.meta['details']
            finalresult.update(oe_det)
            jsonresults = json.dumps(finalresult)
            item  = json.loads(jsonresults)
            logging.info('yielded items are...{}'.format(item))
            yield item
        else:
            logging.info('There are no details found on this page')
            finalresult = response.meta['details']
            jsonresults = json.dumps(finalresult)
            item  = json.loads(jsonresults)
            yield item

