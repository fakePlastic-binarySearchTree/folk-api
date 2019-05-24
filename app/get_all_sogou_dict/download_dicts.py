import requests
import os
from multiprocessing import Pool, freeze_support


def safe_name_for_windows(s):
    chars = '\\/:*?"<>|'
    for c in chars:
        s = s.replace(c, '_')
    return s


def mkdir(path):
    try:
        os.mkdir(path)
    except:
        pass


def download(url: str, filename: str):
    chunk_size = 4096
    with open(filename, 'wb') as f:
        r = requests.get(url)
        for chunk in r.iter_content(chunk_size):
            f.write(chunk)
    print(f'download {filename} success')


if __name__ == '__main__':
    freeze_support()

    all_dict_file = 'all_dict.txt'
    savepath = './data'
    mkdir(savepath)

    pool = Pool(processes=8)
    with open(all_dict_file, 'r') as f:
        for line in f:
            category, name, url = line.strip().split('||')
            name = safe_name_for_windows(name)
            path = os.path.join(savepath, category)
            mkdir(path)
            pool.apply_async(download, (url, os.path.join(path, f'{name}.scel')))

    pool.close()
    pool.join()
