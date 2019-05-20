import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

from api.baidu.objects import SearchResultItem
from utils.util import extract_datetime


class BaiduSearch(object):
    def __init__(self):
        self.url = 'https://www.baidu.com/s'

    def search(self, wd: str, page: int=1):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        params = {
            'wd': wd,
            'pn': (page - 1) * 10,
        }
        items = []
        r = requests.get(self.url, params=params, headers=headers, timeout=5000)
        soup = BeautifulSoup(r.content, 'lxml')
        results = soup.select('.c-container')
        for result in results:
            title_dom = result.select('h3>a')[0]
            abstract_dom = result.select('.c-abstract')
            if len(abstract_dom) == 0:
                abstract_dom = result.select('.c-span-last')
            if len(abstract_dom) > 0:
                abstract_dom = abstract_dom[0]
            else:
                abstract_dom = None

            item = SearchResultItem()
            item.title = title_dom.get_text()
            if abstract_dom:
                item.abstract = abstract_dom.get_text()
                if item.abstract.find('\xa0-\xa0') != -1:
                    item.datetime = extract_datetime(item.abstract.split('\xa0-\xa0')[0])
            item.baidu_url = title_dom['href']
            try:
                item.real_url = requests.head(item.baidu_url).headers['Location']
            except:
                pass
            items.append(item)
        return items
