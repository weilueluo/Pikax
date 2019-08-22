# Pikax:unicorn:
![GitHub stars](https://img.shields.io/github/stars/Redcxx/pikax?color=000&style=flat-square) ![PyPI](https://img.shields.io/pypi/v/pikax?color=000&style=flat-square) ![PyPI - License](https://img.shields.io/pypi/l/pikax?color=000&style=flat-square) ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Redcxx/pikax?color=000&style=flat-square) ![GitHub last commit](https://img.shields.io/github/last-commit/Redcxx/pikax?color=000&style=flat-square) ![PyPI - Downloads](https://img.shields.io/pypi/dw/pikax?color=000&style=flat-square)<br>
Pikax's aim is to provide a simple yet powerful [Pixiv](https://www.pixiv.net/) mass download tool
#### [Chinese ver](https://github.com/Redcxx/Pixiv-Crawler/blob/master/README.md)
````
  # the current v2 is not compatiable with v1, please upgrade carefully, deprecated folder contains v1's source code
  pip install Pikax # current release
````
![demo-gif](https://github.com/Redcxx/Pikax/blob/master/demo.gif)
---
### [GUI version](https://github.com/Redcxx/Pikax/blob/master/gui/dist/Pikax%20-%20Pixiv%20Downloader.exe), note: currently it is unstable
---
# Requirements
- [Python3](https://www.python.org/downloads/)
- [Requests](https://2.python-requests.org/en/master/)
- A network that can reach [Pixiv](https://www.pixiv.net/)
```
  pip install requests
```
# Currently supported features
- Search
  - keyword/tags, limit, type, mode, popularity
- Ranking
  - mode, limit, date, content
- Yours or others
  - illustrations, mangas, bookmarks
- Multiprocessing & multithreading download


# Features incoming
- Search Artists
- Filter Artworks/Artists
- ...
- Tell me!
# Try [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
### Download today's top 50 illustration
```
  from pikax.pikax import Pikax

  pixiv = Pikax()
  results = pixiv.rank(limit=50)
  pixiv.download(results)
```
### Search and download 50 arknights related illustrations with 1000 likes (approx)
```
  from pikax.pikax import Pikax, settings, params

  pixiv = Pikax(settings.username, settings.password)
  results = pixiv.search(keyword='arknights', limit=50, popularity=1000, match=params.Match.PARTIAL)
  pixiv.download(results)
```
### Download user's artworks (required username and password [settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/pikax/settings.py) contains a temp account)
```
  from pikax.pikax import Pikax, settings, params

  # yours
  pixiv = Pikax()
  user = pixiv.login(username=settings.username, password=settings.password)  # login
  bookmarks = user.bookmarks(limit=20)  # get bookmarks
  pixiv.download(bookmarks)  # download

  # any user
  pixiv = Pikax()
  pixiv = Pikax(settings.username, settings.password)
  other_user = pixiv.visits(user_id=201323)  # get user from id

  illusts = other_user.illusts(limit=25)  # get his illustrations
  pixiv.download(illusts)  # download

  mangas = other_user.mangas(limit=10)  # get his mangas
  pixiv.download(mangas)  # download

  bookmarks = other_user.bookmarks(limit=20)  # get his bookmarks
  pixiv.download(bookmarks)  # download
```
### download by id
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  pixiv.download(illust_id=75608670)
````
### Visits [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py) for more examples
### Visits [models.py](https://github.com/Redcxx/Pikax/blob/master/pikax/models.py) for more details on usage

# More operations
### download top 50 of daily ranking and remove artworks with likes <= 1000
````
  from pikax.pikax import Pikax

  pixiv = Pikax()
  results = pixiv.rank(limit=50)  # top 50 ranking

  new_results = results.bookmarks > 1000  # remove likes less than 1000
  pixiv.download(new_results)  # download
````

### download 200 '初音' related, around 1000 bookmarks r18 artworks
### remove artworks with likes >= 1000 and views < 50000
````
  from pikax.pikax import Pikax, settings

  pixiv = Pikax(settings.username, settings.password)
  results = pixiv.search(keyword='初音', limit=200, popularity=1000)  # search

  new_results = (results.bookmarks > 1000).views > 20000  # get likes > 1000 and views > 20000
  pixiv.download(new_results)  # download
````
### visits[models.py](https://github.com/Redcxx/Pikax/blob/master/pikax/models.py) for more operations
### For customization visits [settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/pikax/settings.py)
---
# Note to v1 users
 - I removed some functions such as configure r18 settings and dimension options for search, this is because in order to solve the login issue, I had to use an Android login entry point which does not support as much functionalities as the web logged user does. So in order to provide a consistent interface, I decided to remove them. Although I had found a way to solve the login issue of web, but it require a lot time to implement the technique and it requires a extra dependency, I am still a student and need to study ... I will try to fix them in the future when I am free, no guarantee though ...
 - Instead of using string as parameters now I created params.py which contains enums covering almost all input parameters
 - A brand new download printing is introduced for better ux, instead of popping out skips in the process, they will pop out together at the end, and now it has a est. time left
 # You can reach me by [email](mailto:weilue.luo@student.manchester.ac.uk)
