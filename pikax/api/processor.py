from .models import BaseIDProcessor
from .artwork import Illust
from ..exceptions import ArtworkError


class BaseBaseIDProcessor(BaseIDProcessor):

    def __init__(self):
        super().__init__()

    def process_gifs(self, ids):
        raise NotImplementedError

    def process_mangas(self, ids):
        # they are essentially the same, just illust with more pages
        return self.process_illusts(ids)

    def process_illusts(self, ids):
        successes = []
        fails = []

        for illust_id in ids:
            try:
                successes.append(Illust(illust_id))
            except ArtworkError as e:
                fails.append(illust_id)

        return successes, fails

    def process_novels(self, ids):
        raise NotImplementedError


def main():
    url = ' https://www.pixiv.net/novel/show.php?'
    params = {
        'id': '11333888'
    }
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    from .. import util
    res = util.req(url=url, params=params)
    import re
    author_id = re.search(r'pixiv.context.userId = "(\d*?)"', res.text).group(1)
    print('author_id', author_id)
    url = f'https://www.pixiv.net/ajax/user/{author_id}/profile/novels?'
    id = 11052804
    print('id', id)
    params = {
        'ids[]': id
    }
    res = util.req(url=url, params=params)
    data = res.json()
    util.print_json(data)
    title = data['body']['works'][str(id)]['title']
    username = data['body']['works'][str(id)]['userName']
    bookmarks = data['body']['works'][str(id)]['bookmarkCount']
    print(title)
    print(username)
    print(bookmarks)


if __name__ == '__main__':
    main()