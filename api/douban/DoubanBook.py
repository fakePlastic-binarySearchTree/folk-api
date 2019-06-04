import requests
from bs4 import BeautifulSoup
import re

from api.douban.objects import Book, BookListResp, BookSortType
from utils.util import extract_datetime
from utils.exceptions import AntiSpiderException


class DoubanBook(object):
    def __init__(self, proxies=None):
        self.url = 'https://book.douban.com'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.timeout = 5
        self.proxies = proxies

    def set_proxies(self, proxies):
        self.proxies = proxies

    def get_all_tags(self):
        """
        获取豆瓣图书标签
        :return: [(tag_name, tag_url), ...]
        """
        r = self._requests_get(f'{self.url}/tag/')
        # r = requests.get(f'{self.url}/tag/', headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(r.content, 'lxml')
        result = []
        for dom in soup.select('.article table a'):
            if dom.has_attr('href'):
                result.append((dom.get_text(), self.url + dom['href']))
        return result

    def get_book_list(self, tag_name: str, page: int = 1, sort_type: BookSortType = BookSortType.Composite):
        """
        获取图书列表
        :param tag_name: 标签名
        :param page: 页码
        :param sort_type: 排序规则
        :return: BookListResp
        """
        resp = BookListResp()
        resp.book_list = []
        params = {
            'start': (page - 1) * 20,
            'type': sort_type.value,
        }
        r = self._requests_get(f'{self.url}/tag/{tag_name}', params=params)
        # r = requests.get(f'{self.url}/tag/{tag_name}', params=params, headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(r.content, 'lxml')
        for dom in soup.select('.subject-list .subject-item'):
            book = Book()
            book.title_page_img = dom.select('.pic a img')[0]['src']
            title_dom = dom.select('h2 a')[0]
            book.title = title_dom['title']
            book.detail_url = title_dom['href']
            pub_items = list(map(lambda s: s.strip(), dom.select('.pub')[0].get_text().split(' / ')))

            def handle_author(author):
                result = re.findall(r'[\[\(（【](\w+)[\]\)）】]\s*(\w+)', author)
                if len(result) > 0:
                    book.author_attr, book.author = result[0]
                else:
                    book.author = author

            if len(pub_items) == 4:
                author, book.press, pub_time, book.price = pub_items
                handle_author(author)
                book.public_time = extract_datetime(pub_time)
            elif len(pub_items) == 5:
                author, translator, book.press, pub_time, book.price = pub_items
                handle_author(author)
                book.translator = translator
                book.public_time = extract_datetime(pub_time)
            elif len(pub_items) == 3:
                author, translator, book.press = pub_items
                handle_author(author)

            try:
                book.rating = float(dom.select('.rating_nums')[0].get_text())  # 会有没有评分的书
                book.rating_population = int(re.findall(r'(\d+)', dom.select('.pl')[0].get_text())[0])
            except:
                pass
            resp.book_list.append(book)

        try:
            if len(soup.select('.paginator .next a')) == 0:
                resp.total_page = int(soup.select('.paginator .thispage')[0].get_text())
                resp.current_page = resp.total_page
            else:
                resp.total_page = int(soup.select('.paginator a')[-2].get_text())
                resp.current_page = int(soup.select('.paginator .thispage')[0].get_text())
        except:
            resp.total_page = 1
            resp.current_page = 1

        return resp

    def _requests_get(self, url, params=None):
        args = {
            'url': url,
            'headers': self.headers,
            'timeout': self.timeout,
        }
        if params:
            args['params'] = params
        if self.proxies:
            args['proxies'] = self.proxies
        r = requests.get(**args)
        if r.text.find('检测到有异常请求从你的 IP 发出') != -1:
            raise AntiSpiderException(f'AntiSpiderException content [{r.text}]')
        if r.text.find('window.location.href') != -1 and r.text.find('sec.douban.com') != -1:
            raise AntiSpiderException(f'AntiSpiderException content [{r.text}]')
        return r
