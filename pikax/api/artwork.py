import os

from .models import Artwork
from .. import util, settings
from ..exceptions import ReqException, ArtworkError
import re


class Illust(Artwork):
    """

    extra properties

    """
    _referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    _details_url = 'https://www.pixiv.net/ajax/illust/'
    _headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self, illust_id):
        super().__init__(illust_id)

        # properties, set after generate details is called
        self._views = None
        self._bookmarks = None
        self._title = None
        self._author = None
        self._likes = None

        # iterator use, set after generate download data is called
        self.__download_urls = None

        # not used, set after generate details is called
        self.__original_url_template = None
        self.__comments = None

        # internal uses
        self.__page_count = None
        self._details_url = Illust._details_url + str(self.id)
        self._headers = Illust._headers.copy()
        self._headers['referer'] = Illust._referer_url + str(self.id)

    def config(self):
        try:
            illust_data = util.req(type='get', url=self._details_url, log_req=False).json()
            illust_data = illust_data['body']

            # properties
            self._views = illust_data['viewCount']
            self._bookmarks = illust_data['bookmarkCount']
            self._likes = illust_data['likeCount']
            self._title = illust_data['illustTitle']
            self._author = illust_data['userName']

            self.__original_url_template = illust_data['urls']['original']
            self.__original_url_template = re.sub(r'(?<=_p)\d', '{page_num}', self.__original_url_template)
            self.__comments = illust_data['commentCount']
            self.__page_count = illust_data['pageCount']

            self.__generate_download_data()
        except (ReqException, KeyError) as e:
            raise ArtworkError(f'Failed to configure artwork of id: {self.id}') from e

    def _get_download_url(self, page_num):
        return self.__original_url_template.format(page_num=page_num)

    def _get_download_filename(self, download_url, folder=None):
        id_search = re.search(r'(\d{8}_p\d.*)', download_url)
        illust_signature = id_search.group(1) if id_search else download_url
        filename = str(self.author) + '_' + str(illust_signature)
        if folder is not None:
            filename = os.path.join(util.clean_filename(folder), filename)
        return util.clean_filename(filename)

    def __generate_download_data(self):
        self.__download_urls = []
        curr_page = 0

        while curr_page < self.__page_count:
            if self._reached_limit_in_settings(curr_page):
                break
            self.__download_urls.append(self._get_download_url(curr_page))
            curr_page += 1

    def __getitem__(self, index):
        download_url = self.__download_urls[index]
        filename = self._get_download_filename(download_url)

        return Artwork.DownloadStatus.OK, (download_url, self._headers), filename

    def __len__(self):
        return len(self.__download_urls)

    @property
    def bookmarks(self):
        return self._bookmarks

    @property
    def views(self):
        return self.views

    @property
    def author(self):
        return self._author

    @property
    def title(self):
        return self._title

    @property
    def likes(self):
        return self._likes

    @staticmethod
    def _reached_limit_in_settings(current):
        if settings.MAX_PAGES_PER_ARTWORK:
            if current >= settings.MAX_PAGES_PER_ARTWORK:
                return True
        return False


class Novel(Artwork):
    _content_url = 'https://www.pixiv.net/novel/show.php?'
    _novel_details_url = 'https://www.pixiv.net/ajax/user/{author_id}/profile/novels?'

    def __init__(self, novel_id):
        super().__init__(novel_id)

        # interface
        self._views = None
        self._author = None
        self._title = None
        self._bookmarks = None

        # private
        self.__filename = None
        self.__content = None
        self.__status = None

        # internal
        self.__author_id = None

    def __generate_details_from_content_url(self):
        params = {
            'id': self.id
        }

        res = util.req(url=self._content_url, params=params)

        novel_text_search = re.search(r'id="novel_text">(.*?)</textarea>', res.text, re.S)
        if novel_text_search:
            novel_text = re.sub(r'\[newpage\]', '', novel_text_search.group(1))
        else:
            novel_text = 'Please Login before viewing R18 content'  # mostly due to it is a R18 novel and without login

        self.__content = novel_text
        self.__author_id = re.search(r'pixiv.context.userId = "(\d*?)"', res.text).group(1)
        search = re.findall(r'<span class="views">(.*?)</span>', res.text)
        self._views = search[0]
        self._likes = search[1]

    def __generate_details_from_ajax_url(self):
        novel_details_params = {
            'ids[]': self.id
        }
        novel_details_url = Novel._novel_details_url.format(author_id=self.__author_id)
        novel_data = util.req(url=novel_details_url, params=novel_details_params).json()
        novel_data = novel_data['body']['works']

        if novel_data:
            novel_data = novel_data[str(self.id)]
            self._title = novel_data['title']
            self._author = novel_data['userName']
            self._bookmarks = novel_data['bookmarkCount']

            self.__status = Artwork.DownloadStatus.OK
            self.__filename = self._get_filename()

        else:  # mostly due to it is a R18 novel and without login
            self.__status = Artwork.DownloadStatus.FAILED
            self.__filename = f'Login is required to view R18 novel of id: {self.id}'

    def config(self):
        try:
            self.__generate_details_from_content_url()
            self.__generate_details_from_ajax_url()
        except ReqException as e:
            raise ArtworkError(f'Failed to configure artwork of id: {self.id}') from e

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
    def bookmarks(self):
        return self._bookmarks

    @property
    def likes(self):
        return self._likes

    def __getitem__(self, index):
        if index == 0:
            return self.__status, self.__content, self.__filename
        else:
            raise StopIteration

    def __len__(self):
        return 1


def main():
    from .androidclient import AndroidAPIClient
    from .. import settings
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    client = AndroidAPIClient(settings.username, settings.password)
    # print('Testing Illust Artwork')
    # user = client.visits(user_id=2957827)
    # illust_ids = user.illusts()
    # artworks = [Illust(illust_id) for illust_id in illust_ids]
    # for artwork in artworks:
    #     for status, content, filename in artwork:
    #         print(status, filename)

    # print('Testing Novel Artwork')
    # novel_user = client.visits(22369836)
    # novel_ids = novel_user.novels()
    # novels = [Novel(novel_id) for novel_id in novel_ids]
    # for novel in novels:
    #     for status, text, filename in novel:
    #         print(status, filename)

    novel = Novel(11379546)
    print('bookmarks', novel.bookmarks)
    print('views', novel.views)
    print('likes', novel.likes)
    print(novel.author)

    # illust = Illust(76098647)
    # print(illust.bookmarks)
    # print(illust._likes)


if __name__ == '__main__':
    main()
