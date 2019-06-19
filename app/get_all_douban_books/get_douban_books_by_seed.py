from gevent import monkey
monkey.patch_all()
import gevent

from api.douban.DoubanBook import DoubanBook
from utils.proxy_helper import ProxyHelper
import os
from queue import Queue
import json

from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, SSLError, ConnectionError
from utils.exceptions import AntiSpiderException, ForbiddenException, NotExistsException


exception_cause_by_proxy = [ProxyError, ConnectTimeout, ReadTimeout, SSLError, ConnectionError, AntiSpiderException, ForbiddenException]
exception_do_not_retry = [ForbiddenException, NotExistsException, AntiSpiderException]
save_queue_snapshot_index = 0
queue_snapshot_filename = 'queue_snapshot'


def run_one(detail_set: set,  # 已经拉过detail的集合
            book_dict: dict,
            q: Queue,
            log_q: Queue,
            separator: str):
    db = DoubanBook()
    ph = ProxyHelper(db.set_proxies, db.get_proxies)
    for exception_type in exception_cause_by_proxy:
        ph.add_exception_cause_by_proxy(exception_type)
    for exception_type in exception_do_not_retry:
        ph.add_exception_do_not_retry(exception_type)
    while not q.empty():
        book_id = q.get()
        if book_id in detail_set:
            print(f'skip book {book_id}')
            continue
        print(f'now try to get {book_id}')
        resp = ph.run(db.get_book_detail, book_id)
        if isinstance(resp, Exception):
            print(f'db.get_book_detail fail. book_id:{book_id}. except {resp}')
            if isinstance(resp, NotExistsException):
                detail_set.add(book_id)  # 当做已经爬过，不用再来
            continue
        print(f'get book {resp.book.book_id} {resp.book.title}')
        if book_id in book_dict:
            print(f'book {book_id} has already in book_dict. title {book_dict[book_id]}')
        else:
            log_q.put(f'{resp.book.book_id}{separator}{resp.book.title}\n')
            book_dict[resp.book.book_id] = resp.book.title
        put_new_book = False
        for book in resp.related_books:
            if book.book_id in book_dict:
                continue
            q.put(book.book_id)
            put_new_book = True
        detail_set.add(book_id)
        if put_new_book:
            save_queue_snapshot(queue_snapshot_filename, q)


def write_file(filename: str, log_q: Queue):
    with open(filename, 'a', encoding='utf8') as f:
        while True:
            s = log_q.get()
            if s == '':
                print('write done. exit')
                break
            f.write(s)
            f.flush()


def save_queue_snapshot(filename: str, q: Queue):
    global save_queue_snapshot_index
    save_queue_snapshot_index = 1 - save_queue_snapshot_index
    with open(f'{filename}_{save_queue_snapshot_index}.txt', 'w', encoding='utf8') as f:
        f.write(json.dumps(list(q.queue)))
        f.flush()


def load_queue_snapshot(filename: str, q: Queue):
    filenames = [f'{filename}_{index}.txt' for index in range(2)]
    seeds = set()
    for fn in filenames:
        if os.path.exists(fn):
            with open(fn, 'r', encoding='utf8') as f:
                try:
                    cur_seeds = set(json.loads(f.read()))
                    seeds = seeds | cur_seeds
                except:
                    continue
    for seed in seeds:
        q.put(seed)


def run(filename: str):
    seed_book_id = '1046265'
    q = Queue()
    book_dict = dict()
    detail_set = set()

    separator = ':#:'
    load_queue_snapshot(queue_snapshot_filename, q)
    if q.empty() and os.path.exists(filename):
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                book_id, title = line.strip().split(separator)
                book_dict[book_id] = title
                q.put(book_id)
        print(f'file {filename} contains {len(book_dict)} books')
    if q.empty():
        q.put(seed_book_id)
        print(f'queue is empty. init seed {seed_book_id}')

    log_q = Queue()

    print('now create write file gevent')
    e = list()
    p = gevent.spawn(write_file, filename, log_q)
    for i in range(8):
        e.append(gevent.spawn(run_one, detail_set, book_dict, q, log_q, separator))

    gevent.joinall(e)
    print(f'all done. total books {len(book_dict)}')
    log_q.put('')
    gevent.joinall([p])


if __name__ == '__main__':
    run('get_douban_books_by_seed_result.txt')

