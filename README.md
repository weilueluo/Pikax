# Pixiv-Crawler
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

### 试用
##### 直接运行/修改并运行 [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py) 或者新建文件：
##### 下载当日排行榜前50的插画
````
  """
  Pixiv.rank parameters:
  mode: daily | weekly | monthly | rookie | original | male | female | default daily
  max_page: 1 page = 50 artworks | default all pages
  date: up to which date | default today, format: yyyymmdd
  content: illust | manga | ugoria | default any
  """
  from pixiv import Pixiv
  pixiv = Pixiv()
  results = pixiv.rank(max_page=1, content='illust', mode='daily')
  pixiv.download(results, folder='#Pixiv_daily_ranking')
````
##### 搜索并下载少女相关，赞数约10000的横向插画
````
  """
  Pixiv.search parameters:
  keyword: string to search
  type: manga | illust | ugoira | default any
  dimension: vertical | horizontal | square | default any
  mode: strict_tag | loose | default tag contains
  popularity: a number, add after search keyword as: number users入り | default search all in [500, 1000, 5000, 10000, 20000]
  max_page: 1 page ~ 39 artwork | default all pages
  """
  from pixiv import Pixiv
  pixiv = Pixiv()
  pixiv.download(results)
  results = pixiv.search(keyword='少女', type='illust', dimension='horizontal', popularity=10000)
  pixiv.download(results, folder='#Pixiv_search')
````
##### 下载收藏里的插画（自己的插画需要更改在settings.py里的账号和密码）
````
  """
  Pixiv.favorites:
  username: your pixiv username
  password: your pixiv password
  type: public | private | default both, which of your collections want to save
  """
  #自己的
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  favorites = user.access_favs()
  pixiv.download(favorites)

  #别人的
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  favorites = user.access_favs(pixiv_id=5594793, limit=25)
  pixiv.download(favorites)
````
##### 更多例子请参考[demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
