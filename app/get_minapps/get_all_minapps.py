from api.minapp.MiniApp import MiniApp
import json
import time


def run(output_file: str):
    with open(output_file, 'w', encoding='utf8') as f:
        ma = MiniApp()
        limit = 50
        offset = 0
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} now get offset {offset} limit {limit}')
        result = ma.get_list(offset=offset, limit=limit)
        f.write(json.dumps(result, ensure_ascii=False) + '\n')
        offset += limit
        total = result['meta']['total_count']
        while offset < total:
            print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} now get offset {offset} limit {limit}')
            result = ma.get_list(offset=offset, limit=limit)
            f.write(json.dumps(result, ensure_ascii=False) + u'\n')
            offset += limit


if __name__ == '__main__':
    run('D:/minapps.txt')
