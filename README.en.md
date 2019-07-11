# Pikax:unicorn:
Pikax's aim is to provide a simple yet powerful [Pixiv](https://www.pixiv.net/) mass download tool
#### [Chinese ver](https://github.com/Redcxx/Pixiv-Crawler/blob/master/README.md)
---
### Requirements
- [Python3](https://www.python.org/downloads/)
- [Requests](https://2.python-requests.org/en/master/)
```
  pip install requests
```
### Currently supported download features
- Search
- Ranking
- Favorites
- Artworks
---
### Try [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
#### Download today's top 20 illustration
```
  from pikax import Pixiv

  pixiv = Pixiv()
  results = pixiv.rank(limit=20, content='illust', mode='daily')
  pixiv.download(results, folder='#Pixiv_daily_ranking')
```
#### Search and download 10 horizontal illustrations of keyword: young girl with 10000 likes (approx)
```
  from pikax import Pixiv

  pixiv = Pixiv()
  results = pixiv.search(keyword='少女', type='illust', dimension='horizontal', popularity=10000, limit=10)
  pixiv.download(results)
```
#### Download user's artworks (required username and password [settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/settings.py) contains a temp account)
```
  from pikax import Pixiv

  # yours
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password) # login
  bookmarks = user.bookmarks(limit=20) # get bookmarks
  pixiv.download(bookmarks) # download

  # others
  pixiv = Pixiv()
  user = pixiv.login(settings.username, settings.password) # login

  other_user = user.visits(user_id=3872398) # visit other user by id

  illusts = other_user.illusts(limit=None) # get his illustrations
  pixiv.download(illusts) # download

  mangas = other_user.mangas(limit=5) # get his mangas
  pixiv.download(mangas) # download

  bookmarks = other_user.bookmarks(limit=None) # get his bookmarks
  pixiv.download(bookmarks) # download
```
#### download by artwork id
````
  pixiv = Pixiv()
  pixiv.download(artwork_id=75608670)
````
#### Visit [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py) for more examples and details
