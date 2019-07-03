from pixiv import Pixiv


"""
keyword: string to search
type: manga | illust | ugoira | default any
dimension: vertical | horizontal | square | default any
mode: strict_tag | loose | default tag contains
popularity: a number, add after search keyword as: number users入り | default search all in [500, 1000, 5000, 10000, 20000]
page: which page of the search results to crawl | default all pages
"""


if __name__ == '__main__':
    pixiv = Pixiv()
    results = pixiv.search(keyword='明日方舟', type='illust', dimension='horizontal', popularity=5000)
    pixiv.download(results)
