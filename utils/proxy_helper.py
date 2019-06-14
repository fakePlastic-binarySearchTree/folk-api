import requests
import time
import random


class ProxyHelper(object):
    def __init__(self, set_proxy_func, get_proxy_func):
        self.set_proxy_func = set_proxy_func
        self.get_proxy_func = get_proxy_func
        self.exception_cause_by_proxy = []  # 判定proxy为无效的异常

    def add_exception_cause_by_proxy(self, exception):
        """
        由proxy导致的异常类
        :param exception: 异常类
        :return:
        """
        self.exception_cause_by_proxy.append(exception)

    def run(self, func, *args, **kwargs):
        retry = 10
        while True:
            if not self.get_proxy_func():
                self.set_proxy_func(self._get_proxy())
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retry -= 1
                print(f'there is an exception. retry {retry}. except {e}')
                if retry == 0:
                    if self._exception_cause_by_proxy(e):
                        self._delete_proxy(self.get_proxy_func())
                        self.set_proxy_func(self._get_proxy())
                        retry = 10
                    else:
                        print(f'this exception {type(e)} is not cause by proxy. just skip. {e}')
                        return None

    def _exception_cause_by_proxy(self, exception):
        for exception_type in self.exception_cause_by_proxy:
            if isinstance(exception, exception_type):
                return True
        return False

    def _get_proxy(self):
        while True:
            try:
                r = requests.get('http://127.0.0.1:8000', params={
                    'count': 10,
                })
            except:
                print('cannot reach 127.0.0.1:8000')
                time.sleep(5)
                continue

            proxy_list = r.json()
            if len(proxy_list) > 0:
                break
            else:
                print('no proxy in the pool. just wait...')
                time.sleep(5)
        ip, port, score = random.choice(proxy_list)
        print(f'now get proxy {ip}:{port}')
        return {'https': f'https://{ip}:{port}'}

    def _delete_proxy(self, proxies):
        ip, port = proxies['https'].split('//')[1].split(':')
        r = requests.get('http://127.0.0.1:8000/delete', params={'ip': ip, 'port': port})
        print(f'delete proxy {ip}:{port}. result {r.text}')
