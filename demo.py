"""
Pikax.search:
keyword: string to search
type: manga | illust | default any
dimension: vertical | horizontal | square | default any
mode: strict_tag | loose | default tag contains
popularity: a number, add after search keyword as: number users入り, use 'popular' if you want to get better results | default date descending, all results, which is not as good usually
limit: how many artworks to get | default all


Pikax.rank:
mode: daily | weekly | monthly | rookie | default daily # has problem: | male | female | original
limit: number of artworks to search | default all
date: up to which date | default today, string format: yyyymmdd or python datetime object
content: illust | manga | default any

Pikax.favorites:
username: your pixiv username
password: your pixiv password
type: public | private | default both, which of your collections want to save
"""

from pikax.pikax import Pikax, settings

def download_daily_rankings_example():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password) # optional, but strongly suggested
    results = pixiv.rank(limit=100, content='illust', type='daily', date=None)
    pixiv.download(results, folder='#Pikax_daily_ranking')

def download_search_example():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password) # optional, but strongly suggested
    results = pixiv.search(keyword='オリジナル', type='illust', dimension='horizontal', popularity=10000, limit=20, match=None, mode='safe')
    pixiv.download(results)

def download_other_user_items_example():
    pixiv = Pikax()

    # not suggested
    # other_user = pixiv.access(user_id=201323)

    # suggested
    user = pixiv.login(settings.username, settings.password) # login
    other_user = user.visits(user_id=201323) # visit other user by id

    illusts = other_user.illusts(limit=25) # get his illustrations
    pixiv.download(illusts) # download

    mangas = other_user.mangas(limit=10) # get his mangas
    pixiv.download(mangas) # download

    bookmarks = other_user.bookmarks(limit=20) # get his bookmarks
    pixiv.download(bookmarks) # download

def download_own_bookmarks_example():
    pixiv = Pikax()
    user = pixiv.login(username=settings.username, password=settings.password) # login
    bookmarks = user.bookmarks(limit=20) # get bookmarks
    pixiv.download(bookmarks) # download

def download_by_artwork_id_example():
    pixiv = Pikax()
    pixiv.download(artwork_id=75530638)


def download_r18_ranking_example():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password)
    res = pixiv.rank(type='daily',limit=50, mode='r18')
    pixiv.download(res)

def download_r18_search_example():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password)
    res = pixiv.search(keyword='miku', type='illust', limit=50, mode='r18')
    pixiv.download(res)

def download_with_filter_example():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password) # login
    results = pixiv.rank(limit=50) # top 50 daily ranking

    new_results = results.likes > 1000 # filters likes > 1000
    pixiv.download(new_results) # download

def download_with_filter_example2():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password) # login
    results = pixiv.search(keyword='初音', limit=200, mode='r18', popularity=1000) # search
    
    new_results = (results.likes > 1000) - (results.views < 50000) # get likes > 1000 and remove views < 50000
    pixiv.download(new_results) # download

def main():
    download_daily_rankings_example()
    download_search_example()
    download_own_bookmarks_example()
    download_other_user_items_example()
    download_by_artwork_id_example()
    download_r18_search_example()
    download_r18_ranking_example()
if __name__ == '__main__':
    main()
