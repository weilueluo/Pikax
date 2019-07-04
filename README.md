# Pixiv-Crawler

### 依赖
- Python3
- Requests

### 目前支持的功能
- 搜索
- 排行榜

### 试用
##### 直接运行 crawler.py 或者新建文件：
##### 下载当日排行榜内容
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
##### 搜索并下载内容
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
