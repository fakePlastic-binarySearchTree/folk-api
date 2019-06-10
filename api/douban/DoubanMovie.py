import requests

from api.douban.objects import MovieSortType, Movie
from utils.exceptions import AntiSpiderException


class DoubanMovie(object):
    def __init__(self, proxies=None):
        self.url = 'https://movie.douban.com'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.timeout = 5
        self.proxies = proxies

    def set_proxies(self, proxies):
        self.proxies = proxies

    def get_movie_list(self, tags: list = [], genres: str = None, countries: str = None, year_range: tuple = None, page: int = 1, sort_type: MovieSortType = MovieSortType.Hot):
        """
        获得影视列表
        :param tags: [电影/电视剧/综艺/动漫/纪录片/短片] || [经典/青春/文艺/搞笑/励志/魔幻/感人/女性/黑帮/...]
        :param genres: [剧情/喜剧/动作/爱情/科幻/动画/悬疑/惊悚/恐怖/犯罪/同性/音乐/歌舞/传记/历史/战争/西部/奇幻/冒险/灾难/武侠/情色]
        :param countries: [中国大陆/美国/香港/台湾/日本/韩国/英国/法国/德国/意大利/西班牙/印度/泰国/俄罗斯/伊朗/加拿大/澳大利亚/爱尔兰/瑞典/巴西/丹麦]
        :param year_range: (begin_year, end_year)
        :return: list(Movie)
        """
        url = self.url + '/j/new_search_subjects'
        params = dict()
        params['sort'] = sort_type.value
        params['range'] = '0,10'
        params['tags'] = ','.join(tags)
        params['start'] = (page - 1) * 20
        if genres:
            params['genres'] = genres
        if countries:
            params['countries'] = countries
        if year_range:
            params['year_range'] = ','.join(list(map(lambda s: str(s), year_range)))
        r = self._requests_get(url, params=params)
        data = r.json()
        resp = []
        for item in data['data']:
            movie = Movie()
            movie.directors = item.get('directors', [])
            movie.rate = float(item.get('rate', '0')) if item.get('rate', '0') != '' else 0.0
            movie.title = item.get('title', '')
            movie.url = item.get('url', '')
            movie.casts = item.get('casts', [])
            movie.id = item.get('id')
            resp.append(movie)
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
