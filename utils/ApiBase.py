import requests


class ApiBase(object):
    proxies: dict = None
    headers: dict = None
    timeout: int = None

    def set_proxies(self, proxies: dict):
        self.proxies = proxies

    def get_proxies(self):
        return self.proxies

    def set_headers(self, headers: dict):
        self.headers = headers

    def get_headers(self):
        return self.headers

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def get_timeout(self):
        return self.timeout

    def set_user_agent(self, ua: str):
        if self.headers is None:
            self.headers = {'User-Agent': ua}
        else:
            self.headers['User-Agent'] = ua

    def get_user_agent(self):
        if self.headers is None:
            return None
        else:
            return self.headers.get('User-Agent', None)

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
