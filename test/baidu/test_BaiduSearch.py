from api.baidu.BaiduSearch import BaiduSearch

if __name__ == '__main__':
    baidu = BaiduSearch()
    results = baidu.search('麦肯锡 一诺', page=2)
    for result in results:
        print(result)
