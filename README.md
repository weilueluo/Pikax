# Pikax:unicorn:
Pikax的目的是提供一个使用简单且强大的[Pixiv](https://www.pixiv.net/)\[P站\]批量下载工具。
#### [English ver](https://github.com/Redcxx/Pixiv-Crawler/blob/master/README.en.md)
---
### 需要
- [Python3](https://www.python.org/downloads/)
- [Requests](https://2.python-requests.org/en/master/)
- 可以访问Pixiv的网络
```
  pip install requests
```
### 目前支持的下载功能
- 搜索
  - 关键字/标签，数量，类别，尺寸，模式，受欢迎程度
- 排行榜
  - 日期，数量，模式，内容种类
- 收藏 （需要登录）
  - 你的或者别人的
- 作品 （需要登录）
  - 你的或者别人的
- 多核多线程下载

### 在计划中的功能
- R18作品
- 搜索画师
- 作品/画师 过滤
- 。。。
---
### 试用 [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
#### 下载当日排行榜前20的插画
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  results = pixiv.rank(limit=20, content='illust', mode='daily')
  pixiv.download(results, folder='#Pixiv_daily_ranking')
````
#### 搜索并下载少女相关，赞数约10000的10张横向插画
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  results = pixiv.search(keyword='少女', type='illust', dimension='horizontal', popularity=10000, limit=10)
  pixiv.download(results)
````
#### 下载用户的作品 （需要登录，[settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/settings.py)有临时的账号）
````
  from pikax.pikax import Pikax

  # 自己的
  pixiv = Pikax()
  user = pixiv.login(username=settings.username, password=settings.password) # 登录
  bookmarks = user.bookmarks(limit=20) # 获取收藏
  pixiv.download(bookmarks) # 下载

  # 别人的
  pixiv = Pikax()
  user = pixiv.login(settings.username, settings.password) # 登录

  other_user = user.visits(user_id=3872398) # 访问其他用户

  illusts = other_user.illusts(limit=None) # 获取他的画作
  pixiv.download(illusts) # 下载

  mangas = other_user.mangas(limit=5) # 获取他的漫画
  pixiv.download(mangas) # 下载

  bookmarks = other_user.bookmarks(limit=None) # 获取他的收藏
  pixiv.download(bookmarks) # 下载
````

#### 用作品id下载
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  pixiv.download(artwork_id=75608670)
````
#### 更多例子和详情请参考[demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
