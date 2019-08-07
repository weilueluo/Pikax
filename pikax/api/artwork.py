import os

from .interface import Artwork
from .. import util, settings
from ..exceptions import ReqException, ArtworkError
import re


class Illust(Artwork):
    _referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    _details_url = 'https://www.pixiv.net/ajax/illust/'
    _headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self, illust_id):
        self.id = illust_id

        # properties, set after generate details is called
        self._views = None
        self._likes = None
        self._title = None
        self._author = None

        # iterator use, set after generate download data is called
        self.download_urls = None

        # not used, set after generate details is called
        self.original_url = None
        self.bookmarks = None
        self.comments = None
        self.original_url = None

        # internal uses
        self.page_count = None
        self._details_url = Illust._details_url + str(self.id)
        self._headers = Illust._headers.copy()
        self._headers['referer'] = Illust._referer_url + str(self.id)

        try:
            self._generate_details()
        except ReqException as e:
            raise ArtworkError(f'Failed to init artwork of id: {self.id}') from e

        # uses details: self.page_count
        self._generate_download_data()

    def _generate_details(self):
        illust_data = util.req(type='get', url=self._details_url, log_req=True).json()
        illust_data = illust_data['body']

        # properties
        self._views = illust_data['viewCount']
        self._likes = illust_data['likeCount']
        self._title = illust_data['illustTitle']
        self._author = illust_data['userName']

        self.original_url = illust_data['urls']['original']
        self.bookmarks = illust_data['bookmarkCount']
        self.comments = illust_data['commentCount']
        self.page_count = illust_data['pageCount']
        self.original_url = re.sub(r'(?<=_p)\d', '{page_num}', self.original_url)

    def _get_download_url(self, page_num):
        return self.original_url.format(page_num=page_num)

    def _get_download_filename(self, download_url, folder=None):
        id_search = re.search(r'(\d{8}_p\d.*)', download_url)
        illust_signature = id_search.group(1) if id_search else download_url
        filename = str(self.author) + '_' + str(illust_signature)
        if folder is not None:
            filename = os.path.join(util.clean_filename(folder), filename)
        return util.clean_filename(filename)

    def _generate_download_data(self):
        self.download_urls = []
        curr_page = 0

        while curr_page < self.page_count:
            if self._reached_limit_in_settings(curr_page):
                break
            self.download_urls.append(self._get_download_url(curr_page))
            curr_page += 1

    def __getitem__(self, index):
        download_url = self.download_urls[index]
        filename = self._get_download_filename(download_url)

        if os.path.exists(filename):
            return Artwork.DownloadStatus.SKIPPED, None, filename

        try:
            return Artwork.DownloadStatus.OK, util.req(url=download_url, headers=self._headers,
                                                       log_req=False).content, filename
        except ReqException as e:
            return Artwork.DownloadStatus.FAILED, download_url, filename

    def __len__(self):
        return len(self.download_urls)

    @property
    def likes(self):
        return self._likes

    @property
    def views(self):
        return self.views

    @property
    def author(self):
        return self._author

    @property
    def title(self):
        return self._title

    @staticmethod
    def factory(illust_id):
        return Illust(illust_id)

    def _reached_limit_in_settings(self, current):
        if settings.MAX_PAGES_PER_ARTWORK:
            if current >= settings.MAX_PAGES_PER_ARTWORK:
                return True
        return False


class Novel(Artwork):

    _content_url = 'https://www.pixiv.net/novel/show.php?'
    _novel_details_url = 'https://www.pixiv.net/ajax/user/{author_id}/profile/novels?'

    def __init__(self, novel_id):
        self.id = novel_id
        self._views = None
        self._author = None
        self._title = None
        self._likes = None

        self._filename = None
        self._content = None
        self._status = None

        # internal use
        self._author_id = None

        try:
            self._generate_details()
        except ReqException as e:
            raise ArtworkError(f'Failed to init Novel of id: {self.id}')

    def _generate_details(self):
        params = {
            'id': self.id
        }

        res = util.req(url=self._content_url, params=params)

        novel_text_search = re.search(r'id="novel_text">(.*?)</textarea>', res.text, re.S)
        if novel_text_search:
            novel_text = re.sub(r'\[newpage\]', '', novel_text_search.group(1))
        else:
            novel_text = 'Please Login before viewing R18 content'  # mostly due to it is a R18 novel and without login

        self._content = novel_text
        self._author_id = re.search(r'pixiv.context.userId = "(\d*?)"', res.text).group(1)
        self._views = re.search(r'<span class="views">(.*?)</span>', res.text).group(1)
        novel_details_params = {
            'ids[]': self.id
        }
        novel_details_url = Novel._novel_details_url.format(author_id=self._author_id)
        novel_data = util.req(url=novel_details_url, params=novel_details_params).json()
        novel_data = novel_data['body']['works']

        if novel_data:
            novel_data = novel_data[str(self.id)]
            self._title = novel_data['title']
            self._author = novel_data['userName']
            self._likes = novel_data['bookmarkCount']

            self._status = Artwork.DownloadStatus.OK
            self._filename = self._get_filename()

        else:  # mostly due to it is a R18 novel and without login
            self._status = Artwork.DownloadStatus.FAILED
            self._filename = f'Login is required to view R18 novel of id: {self.id}'


    def _get_filename(self):
        filename = str(self._author) + '_' + str(self.title) + '_' + str(self.id) + '.txt'
        return util.clean_filename(filename)

    @property
    def views(self):
        return self._views

    @property
    def author(self):
        return self._author

    @property
    def title(self):
        return self._title

    @property
    def likes(self):
        return self._likes

    def __getitem__(self, index):
        if index == 0:
            return self._status, self._content, self._filename
        else:
            raise StopIteration

    def __len__(self):
        return 1


def main():
    from .client import Client
    from .. import settings
    client = Client(settings.username, settings.password)
    # print('Testing Illust Artwork')
    # user = client.visits(user_id=2957827)
    # illust_ids = user.illusts()
    # artworks = [Illust(illust_id) for illust_id in illust_ids]
    # for artwork in artworks:
    #     for status, content, filename in artwork:
    #         print(status, filename)

    print('Testing Novel Artwork')
    novel_user = client.visits(13450211)
    novel_ids = novel_user.novels()
    novels = [Novel(novel_id) for novel_id in novel_ids]
    for novel in novels:
        for status, text, filename in novel:
            print(status, filename)



if __name__ == '__main__':
    main()
