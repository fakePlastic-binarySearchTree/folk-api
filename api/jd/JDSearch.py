from utils.ApiBase import ApiBase

import time
import requests
from bs4 import BeautifulSoup
import re


class JDSearch(ApiBase):
    def __init__(self, proxies=None):
        self.url = 'https://search.jd.com/Search'
        self.url_even = 'https://search.jd.com/s_new.php'
        self.set_proxies(proxies)
        self.set_timeout(5000)
        self.set_user_agent('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
        self.set_referer('https://www.jd.com/')

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

    def get_suggestion(self, keyword: str):
        url = 'https://dd-search.jd.com/'
        params = {
            'terminal': 'pc',
            'newjson': 1,
            'ver': 2,
            'zip': 1,
            'key': keyword,
            't': int(time.time() * 1e3),
            'curr_url': 'www.jd.com/',
            'callback': 'f'
        }
        r = self._request_get(url, params=params)
        return r.text[2:-1]

    def _request_get(self, url, params=None, session=None):
        args = {'url': url}
        if params:
            args['params'] = params
        if self.proxies:
            args['proxies'] = self.proxies
        if self.headers:
            args['headers'] = self.headers
        if self.timeout:
            args['timeout'] = self.timeout
        if session:
            r = session.get(**args)
        else:
            r = requests.get(**args)
        return r
