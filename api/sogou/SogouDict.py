import requests
from bs4 import BeautifulSoup
import re

from api.sogou.objects import CategoryInfo, DictInfo, CategoryPageInfo
from utils.util import extract_datetime


class SogouDict(object):
    def __init__(self):
        self.host = 'https://pinyin.sogou.com'
        self.url = 'https://pinyin.sogou.com/dict'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.timeout = 5000

    def get_first_category_list(self):
        """
        获取词库的一级类目
        :return: [CategoryInfo, ...]
        """
        r = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(r.content, 'lxml')
        title_list = soup.select('#dict_category_show')[0].select('.dict_category_list_title ')
        results = []
        for dom in title_list:
            item = CategoryInfo()
            item.name = dom.get_text()
            item.url = self.host + dom.select('a')[0]['href']
            item.category_id = int(re.findall(r'index/(\d+)', item.url)[0])
            results.append(item)
        return results

    def get_by_category_id(self, category_id: int, page: int = 1):
        """
        获取类目id下的详情
        其中sub_categorys只获取二级类目，三级就不要了。毕竟二级就可以搞到所有数据了。
        :param category_id: 类目id
        :param page: 页数
        :return: CategoryPageInfo
        """
        url = self.url + f'/cate/index/{category_id}/default/{page}'
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(r.content, 'lxml')

        result = CategoryPageInfo()

        def get_sub_categorys(soup):
            sub_categorys = []
            first_category_id = int(re.findall(r'index/(\d+)', soup.select('#dict_nav_list .cur_nav a')[0]['href'])[0])

            def extract_category(category_dom):
                category = CategoryInfo()
                map(lambda span: span.clear(), category_dom.select('span'))
                category.name = category_dom.get_text()
                category.url = self.host + category_dom['href']
                category.category_id = int(re.findall(r'index/(\d+)', category.url)[0])
                return category

            def extract_sub_categorys(sub_category_dom, parent_id):
                sc = []
                cate_children_show = sub_category_dom.select('.cate_children_show')
                if len(cate_children_show) > 0:
                    doms = cate_children_show[0].select('td .cate_child_name a')
                    for dom in doms:
                        sub_category = extract_category(dom)
                        sub_category.parent_category_id = parent_id
                        sc.append(sub_category)
                return sc

            if len(soup.select('#select_city_list')) > 0:
                sub_category_dom = soup.select('#select_city_list')[0].parent
                sub_categorys.extend(extract_sub_categorys(sub_category_dom, first_category_id))
            else:
                cate_td_list = soup.select('.cate_words_list td')

                for td in cate_td_list:
                    category = extract_category(td.select('div a')[0])
                    category.parent_category_id = first_category_id
                    sub_categorys.append(category)

            return sub_categorys

        def get_dict_list(detail_dom):
            dict_list = []
            dict_detail_block = detail_dom.select('.dict_detail_block')
            for block in dict_detail_block:
                d = DictInfo()

                title_dom = block.select('.dict_detail_title_block a')[0]
                d.name = title_dom.get_text()
                d.detail_url = self.host + title_dom['href']

                sample, download_times, update_time = block.select('.dict_detail_show .show_content')
                d.sample_words = sample.get_text().split('、')
                d.download_times = int(download_times.get_text())
                d.update_time = extract_datetime(update_time.get_text())

                d.download_url = block.select('.dict_dl_btn a')[0]['href']
                dict_list.append(d)

            return dict_list

        detail_dom = soup.select('#dict_detail_list')[0]
        cate_title = detail_dom.select('.cate_title')[0]
        name, amount = re.findall(r'“(.*?)”分类下共有(\d+)个词库', cate_title.get_text())[0]
        result.name = name
        result.dict_amount = amount

        try:
            dict_page = soup.select('#dict_page')[0]
            result.current_page = int(dict_page.select('.now_page')[0].get_text())
            result.total_page = int(dict_page.select('li')[-2].get_text())
        except:
            result.current_page = 1
            result.total_page = 1

        result.sub_categorys = get_sub_categorys(soup)
        result.dict_list = get_dict_list(detail_dom)

        return result
