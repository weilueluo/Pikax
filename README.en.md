# Pikax:unicorn:
![GitHub stars](https://img.shields.io/github/stars/Redcxx/pikax?color=000&style=flat-square) ![PyPI](https://img.shields.io/pypi/v/pikax?color=000&style=flat-square) ![PyPI - License](https://img.shields.io/pypi/l/pikax?color=000&style=flat-square) ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Redcxx/pikax?color=000&style=flat-square) ![GitHub last commit](https://img.shields.io/github/last-commit/Redcxx/pikax?color=000&style=flat-square) ![PyPI - Downloads](https://img.shields.io/pypi/dm/pikax?color=000&style=flat-square)<br>
&#8593;&#8593;&#8593;&#8593;&#8593;&#8593;&#8593; +1?<br>
Pikax's aim is to provide a simple yet powerful [Pixiv](https://www.pixiv.net/) mass downloading tool
#### [Chinese ver](https://github.com/Redcxx/Pixiv-Crawler/blob/master/README.md)
## GUI
> Does not provide support for using behind The Great FireWall, please use VPN or Airplane 
- [Change log](https://github.com/Redcxx/Pikax/blob/master/gui/dist/change_log.txt)
- Login with your Pixiv account or Guest login
- Support multiprocessing download
  - Rankings
  - Searchings
  - Any user's illustrations/bookmarks/mangas
  - Any artwork
- Language available
  - English (default)
  - Chinese
- [Download here](https://github.com/Redcxx/Pikax/blob/master/gui/dist/latest)
### Building from source（for non-windows user）
> require [pyinstaller](https://www.pyinstaller.org) <br>
> `pip install pyinstaller`
````
git clone https://github.com/Redcxx/Pikax.git
cd Pikax/gui
# change main.spec according to needs
pyinstaller main.spec
cd dist
ls
````
## API
> To prevent block, this api provide multi-threading download but single-core
````
  pip install pikax
````
---
## Requirements
- [Python3](https://www.python.org/downloads/)
- [Requests](https://2.python-requests.org/en/master/)
- A network that can reach [Pixiv](https://www.pixiv.net/)
```
  pip install requests
```
## Currently supported features
- Search
  - keyword/tags, limit, type, mode, popularity
- Ranking
  - mode, limit, date, content
- Yours or others
  - illustrations, mangas, bookmarks


## Features incoming
- Search Artists
- Filter Artworks/Artists
- ...
- Tell me!
## Try [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py)
### Download today's top 50 illustration
```
  from pikax import Pikax

  pixiv = Pikax()
  results = pixiv.rank(limit=50)
  pixiv.download(results)
```
### Search and download 50 arknights related illustrations with 1000 likes (approx)
```
  from pikax import Pikax, settings, params

  pixiv = Pikax(settings.username, settings.password)
  results = pixiv.search(keyword='arknights', limit=50, popularity=1000, match=params.Match.PARTIAL)
  pixiv.download(results)
```
### Download user's artworks (required username and password [settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/pikax/settings.py) contains a temp account)
```
  from pikax import Pikax, settings, params

  # yours
  pixiv = Pikax()
  user = pixiv.login(username=settings.username, password=settings.password)  # login
  bookmarks = user.bookmarks(limit=20)  # get bookmarks
  pixiv.download(bookmarks)  # download

  # any user
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
  from pikax import Pikax

  pixiv = Pikax()
  pixiv.download(illust_id=75608670)
````
### Visits [demo.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/demo.py) for more examples
### Visits [models.py](https://github.com/Redcxx/Pikax/blob/master/pikax/models.py) for more details on usage

## More operations
### download top 50 of daily ranking and remove artworks with likes <= 1000
````
  from pikax import Pikax

  pixiv = Pikax()
  results = pixiv.rank(limit=50)  # top 50 ranking

  new_results = results.bookmarks > 1000  # remove likes less than 1000
  pixiv.download(new_results)  # download
````

### download 200 '初音' related, around 1000 bookmarks r18 artworks
### remove artworks with likes >= 1000 and views < 50000
````
  from pikax import Pikax, settings

  pixiv = Pikax(settings.username, settings.password)
  results = pixiv.search(keyword='初音', limit=200, popularity=1000)  # search

  new_results = (results.bookmarks > 1000).views > 20000  # get likes > 1000 and views > 20000
  pixiv.download(new_results)  # download
````
### For advanced usage visits [advanced demo.py](https://github.com/Redcxx/Pikax/blob/master/advanced%20demo.py)
### For customization visits [settings.py](https://github.com/Redcxx/Pixiv-Crawler/blob/master/pikax/settings.py)
---
 ## You can reach me by [email](mailto:weilue.luo@student.manchester.ac.uk)
