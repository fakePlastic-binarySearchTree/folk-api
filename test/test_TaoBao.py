from api.taobao.Taobao import Taobao


if __name__ == '__main__':
    tb = Taobao()
    resp = tb.search('鼠标 苹果')
    print(resp)
