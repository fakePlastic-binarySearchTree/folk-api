from datetime import datetime
import time
import re


def extract_datetime(s: str):
    try:
        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    except:
        pass

    # x小时前
    result = re.findall(r'(\d+)小时前', s)
    if len(result) > 0:
        n = int(result[0])
        dt = datetime.fromtimestamp(time.time() - n * 3600)
        fmt = '%Y-%m-%d %H'
        return datetime.strptime(dt.strftime(fmt), fmt)

    result = re.findall(r'(\d{4})-(\d{1,2})', s)
    if len(result) > 0:
        year, mon = result[0]
        return datetime.strptime(f'{year}-{mon}', '%Y-%m')

    result = re.findall(r'(\d{1,2})-(\d{1,2})', s)
    if len(result) > 0:
        mon, day = result[0]
        return datetime.strptime(f'{mon}-{day}', '%m-%d')

    result = re.findall(r'(\d{2,4})-(\d+)-(\d+)', s)
    if len(result) > 0:
        year, mon, day = result[0]
        return datetime.strptime(f'{year}-{mon}-{day}', '%Y-%m-%d')

    result = re.findall(r'(\d{2,4})年(\d+)月(\d+)日', s)
    if len(result) > 0:
        year, mon, day = result[0]
        return datetime.strptime(f'{year}-{mon}-{day}', '%Y-%m-%d')

    result = re.findall(r'(\d{4})', s)
    if len(result) > 0:
        year = result[0]
        return datetime.strptime(f'{year}', '%Y')

    return None
