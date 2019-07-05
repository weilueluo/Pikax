# Pixiv-Crawler:unicorn:
#### [Chinese ver](https://github.com/Redcxx/Pixiv-Crawler/blob/master/README.md)
---
### Requirements
- [Python3](https://www.python.org/downloads/)
- [Requests](https://2.python-requests.org/en/master/)
```
  pip install requests
```
### Currently supported features
- Search
- Ranking
- User Favorites
---
### Try => [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
#### Download today's top 50 illustration
```
  from pixiv import Pixiv
  pixiv = Pixiv()
  results = pixiv.rank(max_page=1, content='illust', mode='daily')
  pixiv.download(results, folder='#Pixiv_daily_ranking')
```
#### Search and download horizontal illustration of keyword: young girl with 10000 likes (approx)
```
  from pixiv import Pixiv
  pixiv = Pixiv()
  results = pixiv.search(keyword='少女', type='illust', dimension='horizontal', popularity=10000)
  pixiv.download(results, folder='#Pixiv_search')
```
#### Download artwork in favorites (Change username and password in [settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/settings.py) if you want to download yours)
```
  # yours
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  favorites = user.access_favs()
  pixiv.download(favorites)

  # others
  pixiv = Pixiv()
  user = pixiv.login(username=settings.username, password=settings.password)
  favorites = user.access_favs(pixiv_id=5594793, limit=25)
  pixiv.download(favorites)
```
#### Visit [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py) for more examples and details 
