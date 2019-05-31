from api.douban.DoubanBook import DoubanBook
import requests
import random


def get_proxy():
    r = requests.get('http://127.0.0.1:8000', params={
        'protocol': 1,
        'count': 10,
    })
    ip, port, score = random.choice(r.json())
    return {'https': f'https://{ip}:{port}'}


if __name__ == '__main__':
    proxies = get_proxy()
    print(proxies)
    # db = DoubanBook(proxies=proxies)
    db = DoubanBook()
    print(db.get_all_tags())
    resp = db.get_book_list('外国文学', page=35)
    for book in resp.book_list:
        print(book)
    print(resp.current_page, resp.total_page)
