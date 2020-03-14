from pikax import Pikax, settings, params
from pikax.texts import texts


def download_daily_rankings_example():
    pixiv = Pikax()
    results = pixiv.rank(limit=9)
    pixiv.download(results)


def download_search_example():
    pixiv = Pikax(settings.username, settings.password)
    results = pixiv.search(keyword='arknights', limit=15, popularity=1000, match=params.Match.PARTIAL)
    pixiv.download(results)


def download_other_user_items_example():
    pixiv = Pikax(settings.username, settings.password)

    other_user = pixiv.visits(user_id=201323)  # visit other user by id

    illusts = other_user.illusts(limit=25)  # get his illustrations
    pixiv.download(illusts)  # download

    mangas = other_user.mangas(limit=10)  # get his mangas
    pixiv.download(mangas)  # download

    bookmarks = other_user.bookmarks(limit=15)  # get his bookmarks
    pixiv.download(bookmarks)  # download


def download_own_bookmarks_example():
    pixiv = Pikax()
    user = pixiv.login(username=settings.username, password=settings.password)  # login
    bookmarks = user.bookmarks(limit=15)  # get bookmarks
    pixiv.download(bookmarks)  # download


def download_by_artwork_id_example():
    pixiv = Pikax()
    pixiv.download(illust_id=75530638)


def download_with_filter_example():
    pixiv = Pikax()
    results = pixiv.rank(limit=35)  # top 35 daily ranking

    new_results = results.bookmarks > 1000  # filters likes > 1000
    pixiv.download(new_results)  # download


def download_with_filter_example2():
    pixiv = Pikax(settings.username, settings.password)
    results = pixiv.search(keyword='初音', limit=75, popularity=1000)  # search

    new_results = (results.bookmarks > 1000).views > 20000  # get likes > 1000 and views > 20000
    pixiv.download(new_results)  # download


def main():
    download_daily_rankings_example()
    download_search_example()
    download_own_bookmarks_example()
    download_other_user_items_example()
    # switch to Chinese:
    texts.lang = texts.ZH
    print('Changed language to Chinese')
    download_by_artwork_id_example()
    download_with_filter_example()
    download_with_filter_example2()


if __name__ == '__main__':
    main()
