from api.douban.DoubanBook import DoubanBook
from utils.exceptions import AntiSpiderException
import os
import requests
from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout
import random


def get_proxy():
    r = requests.get('http://127.0.0.1:8000', params={
        'protocol': 1,
        'count': 10,
    })
    ip, port, score = random.choice(r.json())
    print(f'now get proxy {ip}:{port}')
    return {'https': f'https://{ip}:{port}'}


def delete_proxy(db: DoubanBook):
    ip, port = db.proxies['https'].split('//')[1].split(':')
    r = requests.get('http://127.0.0.1:8000/delete', params={'ip': ip, 'port': port})
    print(f'delete proxy {ip}:{port}. result {r.text}')


def db_get_book_list(db: DoubanBook, tag_name: str, page: int = 1):
    retry = 3
    while True:
        if not db.proxies:
            db.set_proxies(get_proxy())
        try:
            return db.get_book_list(tag_name, page=page)
        except (ProxyError, ConnectTimeout, ReadTimeout, AntiSpiderException):
            retry -= 1
            if retry == 0:
                delete_proxy(db)
                db.set_proxies(get_proxy())


def db_get_all_tags(db: DoubanBook):
    retry = 3
    while True:
        if not db.proxies:
            db.set_proxies(get_proxy())
        try:
            return db.get_all_tags()
        except (ProxyError, ConnectTimeout, ReadTimeout, AntiSpiderException):
            retry -= 1
            if retry == 0:
                delete_proxy(db)
                db.set_proxies(get_proxy())


def get_all_books_by_tag(db: DoubanBook, tag_name: str, file_handler):
    print(f'now get books of tag {tag_name}')
    resp = db_get_book_list(db, tag_name)
    for book in resp.book_list:
        file_handler.write(f'{book}\n')
    print(f'now get books of tag {tag_name} page {resp.current_page} total page {resp.total_page}')
    for page in range(2, min(resp.total_page + 1, 51)):  # 好似50页之后豆瓣就不出内容了，什么鬼
        resp = db_get_book_list(db, tag_name, page=page)
        for book in resp.book_list:
            file_handler.write(f'{book}\n')
        print(f'now get books of tag {tag_name} page {resp.current_page} total page {resp.total_page}')


if __name__ == '__main__':
    db = DoubanBook()
    tags = map(lambda item: item[0], db_get_all_tags(db))
    for tag_name in tags:
        filename = f'all_books_{tag_name}.txt'
        if os.path.exists(filename):
            print(f'file {filename} has already exists. skip')
            continue
        with open(filename, 'w', encoding='utf8') as f:
            get_all_books_by_tag(db, tag_name, f)
