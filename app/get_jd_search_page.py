import os
import time
import random
from multiprocessing import Pool, freeze_support

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


def run(input_file: str, output_dir: str):
    try:
        os.mkdir(output_dir)
    except:
        pass
    pool = Pool(processes=10)
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            keyword = line.strip()
            if len(keyword) == 0:
                continue
            pool.apply_async(run_one, (keyword, output_dir))
    pool.close()
    pool.join()


def run_single_process(input_file: str, output_dir: str):
    try:
        os.mkdir(output_dir)
    except:
        pass
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            keyword = line.strip()
            if len(keyword) == 0:
                continue
            run_one(keyword, output_dir)
            sleep_sec = random.random() * random.randint(10, 20)
            print(f'get {keyword} done. sleep {sleep_sec}s')
            time.sleep(sleep_sec)


if __name__ == '__main__':
    # freeze_support()
    run_single_process('D:/ner_list_all_from_predict_res', 'D:/ner_list_all_from_predict_res_result_no_proxy')
    run_single_process('D:/adj_list_all_from_predict_res', 'D:/adj_list_all_from_predict_res_result_no_proxy')
    # run_one('包心丸', 'D:/test_jd')
