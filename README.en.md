# Pixiv-Crawler

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

### Try
#### run/edit&run [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py) directly or create a new python file
##### download today's top 50 illustration
```
  from pixiv import Pixiv
  pixiv = Pixiv()
  results = pixiv.rank(max_page=1, content='illust', mode='daily')
  pixiv.download(results, folder='#Pixiv_daily_ranking')
```
##### search and download horizontal illustration of keyword: young girl with 10000 likes (approx)
```
  """
  from pixiv import Pixiv
  pixiv = Pixiv()
  results = pixiv.search(keyword='少女', type='illust', dimension='horizontal', popularity=10000)
  pixiv.download(results, folder='#Pixiv_search')
```
##### Download artwork in favorites（Need to change username and password in settings.py if you want to download yours）
```
  """
  Pixiv.favorites:
  username: your pixiv username
  password: your pixiv password
  type: public | private | default both, which of your collections want to save
  """
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
#### For more examples visit [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
