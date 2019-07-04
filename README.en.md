# Pixiv-Crawler

### Dependencies
- Python3
- Requests

### Currently supported features
- search
- ranking

### Try
##### run crawler.py directly or create a new python file
##### download today's top 50 illustration
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
##### search and download horizontal illustration of keyword: young girl with 10000 likes (approx)
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
##### download user's favorites
````
  """
  Pixiv.favorites:
  username: your pixiv username
  password: your pixiv password
  type: public | private | default both, which of your collections want to save
  """
  pixiv = Pixiv()
  pixiv.login(username=settings.username, password=settings.password)
  favorites = pixiv.favorites()
  pixiv.download(favorites)
````
