import os
import json

from api.jd.JDSearch import JDSearch
from utils.proxy_helper import ProxyHelper

from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, SSLError, ConnectionError
from utils.exceptions import AntiSpiderException, ForbiddenException, NotExistsException


exception_cause_by_proxy = [ProxyError, ConnectTimeout, ReadTimeout, SSLError, ConnectionError, AntiSpiderException, ForbiddenException]
exception_do_not_retry = [ForbiddenException, NotExistsException, AntiSpiderException]


def run_one(keyword: str, output_dir: str):
    filepath = os.path.join(output_dir, f'{keyword}.html')
    if os.path.exists(filepath):
        print(f'{filepath} has already exists. skip')
        return True

    jd = JDSearch()
    ph = ProxyHelper(jd.set_proxies, jd.get_proxies)
    for exception_type in exception_cause_by_proxy:
        ph.add_exception_cause_by_proxy(exception_type)
    for exception_type in exception_do_not_retry:
        ph.add_exception_do_not_retry(exception_type)

    # content = ph.run(jd.search, keyword)
    content = jd.search(keyword)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def run_suggestion(keyword: str):
    jd = JDSearch()
    suggestion = jd.get_suggestion(keyword)
    print(suggestion)
    print(json.loads(suggestion))


if __name__ == '__main__':
    # run_one('河粉', 'D:/test_jd')
    run_suggestion('河粉')
