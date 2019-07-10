from utils.ApiBase import ApiBase
from bs4 import BeautifulSoup
import re


class MiniApp(ApiBase):
    def __init__(self, proxies=None):
        self.set_user_agent('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
        self.set_timeout(5000)
        self.set_proxies(proxies)

    def get_list(self, offset, limit, tag=None):
        url = 'https://minapp.com/api/v5/trochili/miniapp/'
        params = {
            'limit': limit,
        }
        if offset > 0:
            params['offset'] = offset
        if tag is not None:
            params['tag'] = tag

        r = self._request_get(url, params=params)
        return r.json()
