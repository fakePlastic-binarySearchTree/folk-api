import requests
from bs4 import BeautifulSoup
import re

from api.douban.objects import Book, BookListResp, BookSortType, BookDetailResp
from utils.util import extract_datetime
from utils.exceptions import AntiSpiderException, NotExistsException, ForbiddenException


class DoubanBook(object):
    def __init__(self, proxies=None):
        self.url = 'https://book.douban.com'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.timeout = 5
        self.proxies = proxies

    def set_proxies(self, proxies):
        self.proxies = proxies

    def get_proxies(self):
        return self.proxies

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

            if len(pub_items) == 4:
                author, book.press, pub_time, book.price = pub_items
                self.handle_author(author, book)
                book.public_time = extract_datetime(pub_time)
            elif len(pub_items) == 5:
                author, translator, book.press, pub_time, book.price = pub_items
                self.handle_author(author, book)
                book.translator = translator
                book.public_time = extract_datetime(pub_time)
            elif len(pub_items) == 3:
                author, translator, book.press = pub_items
                self.handle_author(author, book)

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

    def get_book_detail(self, book_id: str):
        """
        书详情，https://book.douban.com/subject/{book_id}/
        :param book_id: 见上
        :return: Book
        """
        log_str = f'book_id:{book_id}'
        url = f'https://book.douban.com/subject/{book_id}/'
        r = self._requests_get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        resp = BookDetailResp()
        resp.book = Book()
        resp.book.book_id = book_id
        try:
            resp.book.title = soup.select('h1 span')[0].get_text()
            log_str = f'{log_str} title:{resp.book.title}'
            resp.book.title_page_img = soup.select('#content .article .subject #mainpic img')[0]['src']
            info_dom = soup.select('#content .article .subject #info')[0]
            info_list_tmp = info_dom.get_text().strip().split(':')
            info_list = []
            for i, s in enumerate(info_list_tmp):
                if i > 0 and i+1 < len(info_list_tmp):
                    l = s.split('\n')
                    info_list.append(' '.join(l[:-1]))
                    info_list.append(l[-1])
                else:
                    info_list.append(s)
            for i in range(0, len(info_list), 2):
                key = info_list[i]
                key = re.sub(r'\s+', ' ', key).strip()
                value = info_list[i+1]
                value = re.sub(r'\s+', ' ', value).strip()
                if key == '作者':
                    self._handle_author(value, resp.book)
                elif key == '出版社':
                    resp.book.press = value
                elif key == '译者':
                    resp.book.translator = value
                elif key == '出版年':
                    resp.book.public_time = extract_datetime(value)
                elif key == '定价':
                    resp.book.price = value
                elif key == 'ISBN':
                    resp.book.ISBN = value
                elif key == '页数':
                    try:
                        resp.book.page_num = int(value)
                    except ValueError as e:
                        result = re.findall(r'(\d+)页', value)
                        if len(result) > 0:
                            resp.book.page_num = int(result[0])
                elif key == '原作名':
                    resp.book.origin_title = value
        except Exception as e:
            print(f'get book info fail. {log_str} {e}')
            if log_str.find('title') == -1:
                print(f'DEBUG: html content {r.text}')

        try:
            resp.book.rating = float(soup.select('#interest_sectl .rating_num')[0].get_text())
            resp.book.rating_population = int(soup.select('#interest_sectl .rating_sum .rating_people span')[0].get_text())
        except Exception as e:
            print(f'get rating fail. {log_str} {e}')
            resp.book.rating = 0.0

        try:
            related_info_dom = soup.select('#content .related_info')[0]
            if len(related_info_dom.select('#link-report .all .intro')) > 0:
                resp.book.description = related_info_dom.select('#link-report .all .intro')[0].get_text()
            else:
                resp.book.description = related_info_dom.select('#link-report .intro')[0].get_text()
        except Exception as e:
            print(f'get description fail. {log_str} {e}')

        resp.related_books = []
        related_dom = soup.select('#db-rec-section')[0]
        for dom in related_dom.select('dl'):
            try:
                book = Book()
                book.title_page_img = dom.select('dt img')[0]['src']
                title_dom = dom.select('dd a')[0]
                book.detail_url = title_dom['href']
                book.title = title_dom.get_text().strip()
                book.book_id = re.findall(r'subject/(.*?)/', book.detail_url)[0]
                resp.related_books.append(book)
            except:
                continue

        return resp

    def _handle_author(self, author: str, book: Book):
        result = re.findall(r'[\[\(（【](\w+)[\]\)）】]\s*(.*)', author)
        if len(result) > 0:
            book.author_attr, book.author = result[0]
        else:
            book.author = author

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
        if r.text.find('<title>页面不存在</title>') != -1:
            raise NotExistsException(f'页面不存在. url:{r.url}')
        if r.text.find('<title>403 Forbidden</title>') != -1:
            raise ForbiddenException('403 Forbidden')
        return r
