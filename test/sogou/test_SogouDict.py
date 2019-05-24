from api.sogou.SogouDict import SogouDict

if __name__ == '__main__':
    sd = SogouDict()
    # fc = sd.get_first_category_list()
    # [print(item) for item in fc]

    result = sd.get_by_category_id(27)
    print(result)
