from datetime import datetime

class SearchResultItem(object):
    title: str = ''
    abstract: str = ''
    baidu_url: str = ''
    real_url: str = ''
    hosts: str = ''
    imgs: list = []
    datetime: datetime = None

    def __str__(self):
        return str(vars(self))
