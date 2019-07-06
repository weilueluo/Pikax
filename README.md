# Pikax:unicorn:
Pikax的目的是提供一个使用简单且强大的[Pixiv](https://www.pixiv.net/)\[P站\]爬取工具。
#### [English ver](https://github.com/Redcxx/Pixiv-Crawler/blob/master/README.en.md)
---
### 需要
- [Python3](https://www.python.org/downloads/)
- [Requests](https://2.python-requests.org/en/master/)
```
  pip install requests
```
### 目前支持的功能
- 搜索
- 排行榜
- 收藏
---
### 试用 [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
#### 下载当日排行榜前50的插画
````
  from pixiv import Pixiv
  
  pixiv = Pixiv()
  results = pixiv.rank(max_page=1, content='illust', mode='daily')
  pixiv.download(results, folder='#Pixiv_daily_ranking')
````
#### 搜索并下载少女相关，赞数约10000的横向插画
````
  from pixiv import Pixiv

  pixiv = Pixiv()
  results = pixiv.search(keyword='少女', type='illust', dimension='horizontal', popularity=10000, max_page=1)
  pixiv.download(results)
````
#### 下载用户的作品（自己的插画需要更改在[settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/settings.py)里的账号和密码）
````
  from pixiv import Pixiv

  # 自己的
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  favorites = user.favs(type='public', limit=20)
  pixiv.download(favorites)

  # 别人的
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  other_user = user.access(pixiv_id=3872398)
  favorites = other_user.favs(limit=25) # 收藏
  pixiv.download(favorites)
  illusts = other_user.illusts(limit=15) # 插画
  pixiv.download(illusts)
  mangas = other_user.mangas(limit=5) # 漫画
  pixiv.download(mangas)
````
#### 更多例子和详情请参考[demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
