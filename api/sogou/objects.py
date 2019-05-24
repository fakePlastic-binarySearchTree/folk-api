from datetime import datetime


class CategoryInfo(object):
    name: str = ''
    url: str = ''
    category_id: int = -1
    parent_category_id: int

    def __str__(self):
        return str(vars(self))


class DictInfo(object):
    name: str = ''
    detail_url: str = ''
    download_url: str = ''
    update_time: datetime = None
    sample_words: list = None
    word_amount: int = 0
    creator: str = ''
    file_size: int = 0
    version: str = ''
    intro: str = ''
    download_times: int = 0

    def __str__(self):
        return str(vars(self))


class CategoryPageInfo(object):
    name: str = ''          # 类目名称，不一定跟FirstCategoryItem.name对应
    dict_amount: int = 0    # 该类目下有多少个词库
    current_page: int = 0   # 当前页
    total_page: int = 0     # 总页数
    dict_list: list = None    # 词典列表
    sub_categorys: list = None   # 子类目

    def __str__(self):
        return str(vars(self))
