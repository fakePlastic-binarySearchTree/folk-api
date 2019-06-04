from datetime import datetime
from enum import Enum


class SortType(Enum):
    Composite = 'T'
    PubTime = 'R'
    Score = 'S'


class Book(object):
    title: str = ''
    author: str = ''
    author_attr: str = ''  # 作者属性，如朝代、国籍
    translator: str = ''
    press: str = ''  # 出版社
    price: str = ''
    public_time: datetime = None
    rating: float = 0  # 豆瓣评分
    rating_population: int = 0  # 评价人数
    description: str = ''
    title_page_img: str = ''
    detail_url: str = ''

    def __str__(self):
        return str(vars(self))


class BookListResp(object):
    book_list: list
    current_page: int
    total_page: int

    def __str__(self):
        return str(vars(self))
