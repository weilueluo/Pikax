> # Under Development, some funtions not available (sad)
# Pikax:unicorn:
Pikax's aim is to provide a simple yet powerful [Pixiv](https://www.pixiv.net/) download tool
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
- User Favorites
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
#### Download user's artworks (Change username and password in [settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/settings.py) if you want to download yours)
```
  from pikax import Pixiv

  # yours
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  favorites = user.favs(type='public', limit=20)
  pixiv.download(favorites)

  # others
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  other_user = user.access(pixiv_id=3872398)
  favorites = other_user.favs(limit=25) # favorites
  pixiv.download(favorites)
  illusts = other_user.illusts(limit=15) # illustrations
  pixiv.download(illusts)
  mangas = other_user.mangas(limit=5) # mangas
  pixiv.download(mangas)
```
#### Visit [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py) for more examples and details
