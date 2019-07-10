"""
Pixiv.search:
keyword: string to search
type: manga | illust | ugoira | default any
dimension: vertical | horizontal | square | default any
mode: strict_tag | loose | default tag contains
popularity: a number, add after search keyword as: number users入り, use 'popular' if you want to get better results | default date descending, all results, which is not as good usually
limit: how many artworks to get | default all


Pixiv.rank:
mode: daily | weekly | monthly | rookie | default daily # has problem: | male | female | original
limit: number of artworks to search | default all
date: up to which date | default today, format: yyyymmdd
content: illust | manga | ugoria | default any
"""

from pikax.pikax import Pixiv, User
from pikax.pikax import settings

def download_daily_rankings_example():
    pixiv = Pixiv()
    results = pixiv.rank(limit=10, content='illust', mode='daily', date=None)
    pixiv.download(results, folder='#Pixiv_daily_ranking')

def download_search_example():
    pixiv = Pixiv()
    results = pixiv.search(keyword='オリジナル', type='illust', dimension='horizontal', popularity=10000, limit=20)
    pixiv.download(results)

def download_other_user_items_example():
    pixiv = Pixiv()
    user = pixiv.login(settings.username, settings.password) # login

    other_user = user.visits(user_id=3872398) # visit other user by id

    illusts = other_user.illusts(limit=25) # get his illustrations
    pixiv.download(illusts) # download

    mangas = other_user.mangas(limit=5) # get his mangas
    pixiv.download(mangas) # download

    bookmarks = other_user.bookmarks(limit=30) # get his bookmarks
    pixiv.download(bookmarks) # download

def download_own_bookmarks_example():
    pixiv = Pixiv()
    user = pixiv.login(username=settings.username, password=settings.password) # login
    bookmarks = user.bookmarks(limit=20) # get bookmarks
    pixiv.download(bookmarks) # download

def download_by_artwork_id_example():
    pixiv = Pixiv()
    pixiv.download(artwork_id=75608670)

def main():
    download_daily_rankings_example()
    download_search_example()
    download_own_bookmarks_example()
    download_other_user_items_example()
    download_by_artwork_id_example()

if __name__ == '__main__':
    main()
