from api.sogou.SogouDict import SogouDict
from api.sogou.objects import CategoryInfo, DictInfo, CategoryPageInfo


def to_str(page_info: CategoryPageInfo, d: DictInfo):
    return f'{page_info.name}||{d.name}||{d.download_url}'


def get_all_category_id(sd: SogouDict):
    category_id_set = set()
    first_category_list = sd.get_first_category_list()
    for category in first_category_list:
        category_id_set.add(category.category_id)
        info = sd.get_by_category_id(category.category_id)
        for sub in info.sub_categorys:
            category_id_set.add(sub.category_id)

    return list(category_id_set)


def get_all_dict_by_category_id(sd: SogouDict, category_id: int, file_handler: None):
    dicts = []
    info: CategoryPageInfo = sd.get_by_category_id(category_id)
    for d in info.dict_list:
        file_handler.write(to_str(info, d) + '\n')
    dicts.extend(info.dict_list)
    total_page = info.total_page
    for page in range(2, total_page + 1):
        info: CategoryPageInfo = sd.get_by_category_id(category_id, page=page)
        for d in info.dict_list:
            file_handler.write(to_str(info, d) + '\n')
        dicts.extend(info.dict_list)
    return dicts


def get_all_dict(sd: SogouDict, all_category_id: list, filename: str):
    dicts = []
    with open(filename, 'w') as f:
        for category_id in all_category_id:
            dicts.extend(get_all_dict_by_category_id(sd, category_id, f))
    return dicts


if __name__ == '__main__':
    sd = SogouDict()
    first_category_list = sd.get_first_category_list()
    category_id = [category.category_id for category in first_category_list]
    dicts = get_all_dict(sd, category_id, 'all_dict.txt')
    print('total cnt', len(dicts))
