from api.douban.DoubanMovie import DoubanMovie
from api.douban.objects import MovieSortType
from utils.exceptions import AntiSpiderException
import os
import requests
from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, SSLError, ConnectionError
import random
import time


def get_proxy():
    while True:
        try:
            r = requests.get('http://127.0.0.1:8000', params={
                'protocol': 1,
                'count': 10,
            })
        except:
            print('cannot reach 127.0.0.1:8000')
            time.sleep(5)
            continue

        proxy_list = r.json()
        if len(proxy_list) > 0:
            break
        else:
            print('no proxy in the pool. just wait...')
            time.sleep(5)
    ip, port, score = random.choice(proxy_list)
    print(f'now get proxy {ip}:{port}')
    return {'https': f'https://{ip}:{port}'}


def delete_proxy(dm: DoubanMovie):
    ip, port = dm.proxies['https'].split('//')[1].split(':')
    r = requests.get('http://127.0.0.1:8000/delete', params={'ip': ip, 'port': port})
    print(f'delete proxy {ip}:{port}. result {r.text}')


def dm_get_movie_list(dm: DoubanMovie, year_range: tuple, area: str, page: int = 1):
    retry = 3
    while True:
        if not dm.proxies:
            dm.set_proxies(get_proxy())
        try:
            return dm.get_movie_list(year_range=year_range, countries=area, page=page, sort_type=MovieSortType.Latest)
        except (ProxyError, ConnectTimeout, ReadTimeout, AntiSpiderException, SSLError, ConnectionError) as e:
            retry -= 1
            print(f'there is an exception. retry {retry}. except {e}')
            if retry == 0:
                delete_proxy(dm)
                dm.set_proxies(get_proxy())
                retry = 3


def get_all_movie_by_year_range(dm: DoubanMovie, year_range: tuple, area: str, file_handler):
    print(f'now get movies of {year_range}')
    for page in range(1, 10000):
        resp = dm_get_movie_list(dm, year_range=year_range, area=area, page=page)
        if len(resp) == 0:
            break
        for movie in resp:
            file_handler.write(f'{movie}\n')
        print(f'now get movies of {year_range} page {page}')


if __name__ == '__main__':
    dm = DoubanMovie()
    years = [(y, y) for y in range(2019, 1999, -1)]
    years.extend([(y, y+9) for y in range(1990, 1959, -10)])
    years.extend([(1, 1959)])
    areas = ['中国大陆', '香港', '台湾']
    for year_range in years:
        for area in areas:
            filename = f'all_movies_{area}_{year_range[0]}_{year_range[1]}.txt'
            if os.path.exists(filename):
                print(f'file {filename} has already exists. skip')
                continue
            with open(filename, 'w', encoding='utf8') as f:
                get_all_movie_by_year_range(dm, year_range, area, f)
