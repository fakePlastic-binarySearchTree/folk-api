import requests
from bs4 import BeautifulSoup
import re

from api.douban.objects import Book, BookListResp
from utils.util import extract_datetime


class DoubanBook(object):
    def __init__(self):
        self.url = 'https://book.douban.com'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.timeout = 5000

    def get_all_tags(self):
        """
        获取豆瓣图书标签
        :return: [(tag_name, tag_url), ...]
        """
        r = requests.get(f'{self.url}/tag/', headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(r.content, 'lxml')
        result = []
        for dom in soup.select('.article a'):
            if dom.has_attr('href'):
                result.append((dom.get_text(), self.url + dom['href']))
        return result

    def get_book_list(self, tag_name: str, page: int = 1):
        """
        获取图书列表
        :param tag_name: 标签名
        :param page: 页码
        :return: BookListResp
        """
        resp = BookListResp()
        resp.book_list = []
        params = {
            'start': (page - 1) * 40,
            'type': 'T'
        }
        r = requests.get(f'{self.url}/tag/{tag_name}', params=params, headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(r.content, 'lxml')
        for dom in soup.select('.subject-list .subject-item'):
            book = Book()
            book.title_page_img = dom.select('.pic a img')[0]['src']
            title_dom = dom.select('h2 a')[0]
            book.title = title_dom['title']
            book.detail_url = title_dom['href']
            pub_items = list(map(lambda s: s.strip(), dom.select('.pub')[0].get_text().split('/')))
            if len(pub_items) == 4:
                author, press, pub_time, price = pub_items
            elif len(pub_items) == 5:
                author, translator, press, pub_time, price = pub_items
                book.translator = translator
            result = re.findall(r'\[(\w+)\]\s*(\w+)', author)
            if len(result) > 0:
                book.author_attr, book.author = result[0]
            else:
                book.author = author
            book.press = press
            book.public_time = extract_datetime(pub_time)
            book.price = price
            book.rating = float(dom.select('.rating_nums')[0].get_text())
            book.rating_population = int(re.findall(r'(\d+)', dom.select('.pl')[0].get_text())[0])
            resp.book_list.append(book)

        return resp
