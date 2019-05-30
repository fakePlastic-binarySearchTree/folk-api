from api.douban.DoubanBook import DoubanBook

if __name__ == '__main__':
    db = DoubanBook()
    # print(db.get_all_tags())
    resp = db.get_book_list('小说')
    for book in resp.book_list:
        print(book)
