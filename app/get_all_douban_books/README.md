## 爬豆瓣图书

 - 豆瓣对ip有限制，于是用上代理池。目前代码里用的是[IPProxyPool](https://github.com/qiyeboy/IPProxyPool)。具体姿势是另外将IPProxyPool运行起来，在本地起一个web server，然后本程序通过http拿到proxy。
 - 对于书的出版信息的获取还不太准。
 - 发现豆瓣50页之后就拿不到东西了，不知道怎么搞全量的书。