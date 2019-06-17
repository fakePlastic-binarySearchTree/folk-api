from gevent import monkey
monkey.patch_all()
import gevent

from api.douban.DoubanBook import DoubanBook
from utils.proxy_helper import ProxyHelper
import os
from queue import Queue

from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, SSLError, ConnectionError
from utils.exceptions import AntiSpiderException, ForbiddenException


exception_cause_by_proxy = [ProxyError, ConnectTimeout, ReadTimeout, SSLError, ConnectionError, AntiSpiderException, ForbiddenException]


def run_one(detail_set: set,  # 已经拉过detail的集合
            book_dict: dict,
            q: Queue,
            log_q: Queue,
            separator: str):
    db = DoubanBook()
    ph = ProxyHelper(db.set_proxies, db.get_proxies)
    for exception_type in exception_cause_by_proxy:
        ph.add_exception_cause_by_proxy(exception_type)
    while not q.empty():
        book_id = q.get()
        if book_id in detail_set:
            print(f'skip book {book_id}')
            continue
        print(f'now try to get {book_id}')
        resp = ph.run(db.get_book_detail, book_id)
        if not resp:
            print(f'db.get_book_detail fail. book_id:{book_id}')
            continue
        print(f'get book {resp.book.book_id} {resp.book.title}')
        if book_id in book_dict:
            print(f'book {book_id} has already in book_dict. title {book_dict[book_id]}')
        else:
            log_q.put(f'{resp.book.book_id}{separator}{resp.book.title}\n')
            book_dict[resp.book.book_id] = resp.book.title
        for book in resp.related_books:
            if book.book_id in book_dict:
                continue
            q.put(book.book_id)
        detail_set.add(book_id)


def write_file(filename: str, log_q: Queue):
    with open(filename, 'a', encoding='utf8') as f:
        while True:
            s = log_q.get()
            if s == '':
                print('write done. exit')
                break
            f.write(s)
            f.flush()


def run(filename: str):
    seed_book_id = '1046265'
    q = Queue()
    book_dict = dict()
    detail_set = set()

    separator = ':#:'
    if os.path.exists(filename):
        seed_q = Queue()
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                book_id, title = line.strip().split(separator)
                book_dict[book_id] = title
                seed_q.put(book_id)
                while seed_q.qsize() > 50:
                    seed_q.get()
        while not seed_q.empty():
            q.put(seed_q.get())
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

