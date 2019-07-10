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

Pixiv.favorites:
username: your pixiv username
password: your pixiv password
type: public | private | default both, which of your collections want to save
"""

from pikax import Pixiv, User
import settings

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
    other_user = pixiv.access(pixiv_id=3872398)
    illusts = other_user.illusts(limit=None)
    pixiv.download(illusts)
    mangas = other_user.mangas(limit=5)
    pixiv.download(mangas)

# def download_own_favourites_example():
#     pixiv = Pixiv()
#     user = pixiv.login(username=settings.username, password=settings.password)
#     favorites = user.favs(type='public', limit=None)
#     pixiv.download(favorites)

def main():
    # download_daily_rankings_example()
    # download_search_example()
    # download_own_favourites_example()
    download_other_user_items_example()

if __name__ == '__main__':
    main()
