from pixiv import Pixiv


"""
keyword: string to search
type: manga | illust | ugoira | default any
dimension: vertical | horizontal | square | default any
mode: strict_tag | loose | default tag contains
popularity: a number, add after search keyword as: number users入り | default date descending
page: which page of the search results to crawl | default 1
"""


if __name__ == '__main__':
    pixiv = Pixiv()
    results = pixiv.search(keyword='少女', popularity=20000, type='illust')
    pixiv.download(results)
