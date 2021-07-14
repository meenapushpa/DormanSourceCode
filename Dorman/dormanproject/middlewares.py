# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
import os
import random
import base64
import logging
import requests
from . import freeproxy
from lxml.html import fromstring
from scrapy import signals
from scrapy.selector import Selector
import scrapy.crawler as crawler
from scrapy.core.downloader.handlers.http11 import TunnelError
from django.db import IntegrityError
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError


class RetryMiddleware(object):
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        print(self.proxy_list)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        settings = crawler.settings
        newproxy = []
        if not settings.getlist('PROXY_LIST'):
            proxylist = str(freeproxy.FreeProxy('url'))
            if proxylist not in newproxy:
                newproxy.append(proxylist)
                proxy_list = proxylist
        else:
            proxy_list = settings.getlist('PROXY_LIST')
        return cls(proxy_list)

    def process_exception(self, request, exception, spider):
        if (isinstance(exception, TimeoutError) or isinstance(exception, TunnelError) or isinstance(exception, ResponseNeverReceived)) \
                and 'dont_retry' not in request.meta:
            request.meta['proxy'] = self.proxy_list
        elif (isinstance(exception, IntegrityError)):
            message = 'Duplicate: %s' % response.url
            logging.info(message)

            return request


class ProxyMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        print('Proxy:',self.proxy_list)
    
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'dormanproject.settings'
        settings = crawler.settings
        newproxy = []
        if not settings.getlist('PROXY_LIST'):
            proxylist = str(freeproxy.FreeProxy('url'))
            if proxylist not in newproxy:
                newproxy.append(proxylist)
                proxy_list = proxylist
        else:
            proxy_list = settings.getlist('PROXY_LIST')
        s = cls(proxy_list)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        
        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.
        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            return
        request.meta['proxy'] = self.proxy_list
        
    def spider_opened(self, spider):
        logging.info('Spider opened: %s' % spider.name)


class DormanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

