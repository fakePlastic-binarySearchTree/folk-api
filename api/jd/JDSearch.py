import requests
from bs4 import BeautifulSoup
import re


class JDSearch(object):
    def __init__(self, proxies=None):
        self.url = 'https://search.jd.com/Search'
        self.url_even = 'https://search.jd.com/s_new.php'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.timeout = 5000
        self.proxies = proxies

    def set_proxies(self, proxies):
        self.proxies = proxies

    def get_proxies(self):
        return self.proxies

    def search(self, keyword: str, page: int = 1):
        """
        :param keyword:
        :param page: 页码，只支持奇数
        :return: (当前奇数页，当前偶数页）
        """
        params = {
            'keyword': keyword,
            'enc': 'utf-8',
        }
        if page % 2 == 0:
            page -= 1
        if page > 1:
            params['page'] = page
        if self.proxies:
            params['proxies'] = self.proxies

        session = requests.session()
        r = self._requests_get(self.url, params=params, session=session)

        return r.content.decode('utf-8')

    def _requests_get(self, url, params=None, session=None):
        args = {
            'url': url,
            'headers': self.headers,
            'timeout': self.timeout,
        }
        if params:
            args['params'] = params
        if self.proxies:
            args['proxies'] = self.proxies
        if session:
            r = session.get(**args)
        else:
            r = requests.get(**args)
        return r
