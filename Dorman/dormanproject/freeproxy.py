import re
import random
import requests
import itertools
from lxml.html import fromstring
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class FreeProxy(object):
    def __init__(self, input=None):
        self.choice = input

    def freeproxylist(self):
        freeurl = 'https://free-proxy-list.net/anonymous-proxy.html'
        freeresponse = requests.get(freeurl, verify=False)
        freeparser = fromstring(freeresponse.text)
        freeproxies = []
        for i in freeparser.xpath('//tbody/tr'):
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                freeproxy = ":".join(
                    [i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                freeproxies.append(freeproxy)
        return freeproxies

    def proxyparse(self, proxy):
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 2:
            ip, port = proxy_parts
            formatted_proxy = {
                'http': f'http://{ip}:{port}/',
            }
            auth = None
        elif len(proxy_parts) == 4:
            ip, port, user, password = proxy_parts
            formatted_proxy = {
                'http': f'http://{user}:{password}@{ip}:{port}/',
            }
            auth = None
        formatted_proxy = formatted_proxy['http']
        return formatted_proxy, auth

    def __repr__(self):
        freeproxy = self.freeproxylist()
        if len(freeproxy) != 0:
            random_pick = random.choice(freeproxy)
            if self.choice == 'url':
                proxylink, auth = self.proxyparse(random_pick)
            else:
                proxylink = random_pick
        else:
            self.__repr__()

        return proxylink


class PaidProxy(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def readproxy(self, input):
        with open(input) as txt_file:
            proxies = txt_file.read().splitlines()
        return proxies

    def __repr__(self):
        proxies = self.readproxy(self.filepath)
        proxy_swm = itertools.cycle(proxies)
        proxy = next(proxy_swm)
        fp = FreeProxy()
        proxyurl, httpauth = fp.proxyparse(proxy)
        return proxyurl


class WriteProxyList(object):
    def fetchandwriteproxy(self, writepath):
        fp = FreeProxy().freeproxylist()
        if len(fp) != 0:
            with open(writepath, 'w') as wp:
                for i in fp:
                    fetchlist, fetchauth = FreeProxy().proxyparse(i)
                    wp.write('%s\n' % fetchlist)
