from api.minapp.MiniApp import MiniApp


if __name__ == '__main__':
    ma = MiniApp()
    result = ma.get_list(10550, 50)
    print(result)
