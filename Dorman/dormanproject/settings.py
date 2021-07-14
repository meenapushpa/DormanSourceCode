# -*- coding: utf-8 -*-

# Scrapy settings for dormanproject project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os
import sys
from datetime import datetime

BOT_NAME = 'dormanproject'

SPIDER_MODULES = ['dormanproject.spiders']
NEWSPIDER_MODULE = 'dormanproject.spiders'


#USER_AGENT_LIST  = os.path.join(os.path.expanduser('~'), "work/DDS_Web/scraper/misc/useragents.txt")
USER_AGENT_LIST = "/root/Dorman/misc/useragents.txt"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'random_useragent.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware':None,
   #'scraper.dormanproject.middlewares.RetryMiddleware':200,
    #'scraper.dormanproject.middlewares.DormanSpiderMiddleware':100,
    'rotating_proxies.middlewares.RotatingProxyMiddleware':200
    #'scraper.dormanproject.middlewares.ProxyMiddleware':100,
    #'scraper.dormanproject.pipelines.StoreInMemoryPipeline': 120,
}
ROTATING_PROXY_LIST_PATH='/root/Dorman/dormanproject/proxyurl.lst'

LOG_LEVEL='INFO'
LOG_LEVEL='DEBUG'



CONCURRENT_REQUESTS = 5
CONCURRENT_REQUESTS_PER_DOMAIN = 5

ITEM_PIPELINES = {
    #'dormanproject.pipelines.DormanproductPipeline':250,
    'dormanproject.pipelines.JsonWriterPipeline':260,
    #'dormanproject.pipelines.InMemoryItemStore':300,
    #'scraper.dormanproject.pipelines.CSVPipeline': 260,
}
#FEED_FORMAT = 'xlsx'
#FEED_URI = 'data/%s.json' % datetime.utcnow().strftime('%Y-%d-%mT%H-%M-%S')  # WHERE to store the export file

DOWNLOAD_TIMEOUT = 60
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 404, 408]

REDIRECT_ENABLED = True
REFERER_ENABLED = False

COOKIES_ENABLED = False
COOKIES_DEBUG = False



#PROXY_LIST = ['http://95.217.186.24:3128/','http://85.14.243.31:3128/','http://161.202.226.194:80/','http://89.187.181.71:3128/']
#if PROXY_LIST:
 #   DOWNLOADER_MIDDLEWARES['scraper.dormanproject.middlewares.RetryMiddleware'] = 200
  #  DOWNLOADER_MIDDLEWARES['scraper.dormanproject.middlewares.ProxyMiddleware'] = 100

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'dormanproject.middlewares.DormanprojectSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'dormanproject.middlewares.DormanprojectDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'dormanproject.pipelines.DormanprojectPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
