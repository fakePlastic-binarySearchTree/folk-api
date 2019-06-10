from api.douban.DoubanMovie import DoubanMovie
from api.douban.objects import MovieSortType


if __name__ == '__main__':
    dm = DoubanMovie()
    resp = dm.get_movie_list()
    for movie in resp:
        print(movie)
