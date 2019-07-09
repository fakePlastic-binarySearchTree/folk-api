import requests
from bs4 import BeautifulSoup


class Taobao(object):
    def __init__(self):
        self.search_url = 'https://s.taobao.com/search'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.timeout = 5000
        self.session = requests.Session()

    def set_cookies(self, ):

    def search(self, query: str):
        params = {
            'q': query,
        }
        r = self._requests_get(self.search_url, params=params)
        return r.text

    def _requests_get(self, url, params=None):
        args = {
            'url': url,
            'headers': self.headers,
            'timeout': self.timeout,
        }
        if params:
            args['params'] = params
        # if self.proxies:
        #     args['proxies'] = self.proxies
        r = self.session.get(**args)
        return r
