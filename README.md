# Pikax:unicorn:
Pikax的目的是提供一个使用简单且强大的[Pixiv](https://www.pixiv.net/)\[P站\]批量下载工具。
#### [English ver](https://github.com/Redcxx/Pixiv-Crawler/blob/master/README.en.md)
````
  pip install Pikax # 当前的预发布
````
---
## 需要
- [Python3](https://www.python.org/downloads/)
- [Requests](https://2.python-requests.org/en/master/)
- 可以访问[Pixiv](https://www.pixiv.net/)的网络
```
  pip install requests
```
### 目前支持的下载功能
- 搜索
  - 关键字/标签，数量，类别，尺寸，模式，受欢迎程度, r18
- 排行榜
  - 日期，数量，模式，内容种类, r18
- 你的或者别人的
  - 插画，漫画，收藏
- 多核多线程下载

### 在计划中的功能
- 搜索画师
- 作品/画师 过滤
- 。。。
- 有人再做吧，我自己够用了owo
---
### 个性化设置请前往[settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/pikax/settings.py)
---
## 试用 [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
> ### 如果没有登录[Pixiv](https://www.pixiv.net/)有可能只返回部分结果
#### 下载当日排行榜前20的插画
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  results = pixiv.rank(limit=20, content='illust', type='daily', mode='safe')
  pixiv.download(results, folder='#Pixiv_daily_ranking')
````
#### 搜索并下载arknights相关，赞数约10000的10张无色情横向插画
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  pixiv.login(settings.username, settings.password)
  results = pixiv.search(keyword='arknights', type='illust', dimension='horizontal', popularity=10000, limit=10, mode='safe', match=None)
  pixiv.download(results)
````
#### 下载用户的作品 （需要登录，[settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/pikax/settings.py)有临时的账号）
````
  from pikax.pikax import Pikax

  # 自己的
  pixiv = Pikax()
  user = pixiv.login(username=settings.username, password=settings.password) # 登录
  bookmarks = user.bookmarks(limit=20) # 获取收藏
  pixiv.download(bookmarks) # 下载

  # 任何用户
  pixiv = Pikax()

  user = pixiv.login(settings.username, settings.password) # 登录
  other_user = user.visits(user_id=3872398) # 以此访问其他用户


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

## 更多操作
#### 下载排行榜前50且赞数高于1000的作品
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  pixiv.login(settings.username, settings.password) # 登录
  results = pixiv.rank(limit=50) # 今日排行榜前50

  new_results = results.likes > 1000 # 过滤赞数大于1000
  pixiv.download(new_results) # 下载
````

#### 搜索'初音'相关的200个收藏约1000的r18作品
#### 并筛选出其中赞大于1000且浏览量大于50000的作品
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  pixiv.login(settings.username, settings.password) # 登录
  results = pixiv.search(keyword='初音', limit=200, mode='r18', popularity=1000) # 搜索
  
  new_results = (results.likes > 1000) - (results.views < 50000) # 过滤
  pixiv.download(new_results) # 下载
````
#### 更多操作请参考[items.PixivResult](https://github.com/Redcxx/Pikax/blob/master/pikax/items.py#L155)
