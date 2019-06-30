import settings
from pixiv import Pixiv


"""
keyword: string to search
type: manga | illust | ugoira | default any
dimension: vertical | horizontal | square | default any
mode: strict_tag | loose | default tag contains
popularity: a number, add after search keyword as: number users入り | default date descending
page: which page of the search results to crawl | default 1

return a list of ArtWork object
"""


if __name__ == '__main__':
    pixiv = Pixiv(settings.username, settings.password)
    results = pixiv.search(keyword='少女', popularity=10000, type='illust', page=2)
    pixiv.download(results)
