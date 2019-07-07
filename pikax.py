# -*- coding: utf-8 -*-

import time, util
import re, sys, os, settings
from multiprocessing import Manager
from pages import SearchPage, RankingPage, LoginPage
from items import Artwork, PixivResult, OtherUser

sys.stdout.reconfigure(encoding='utf-8')

__all__ = ['Pixiv', 'User']

class Pixiv:

    def __init__(self):
        self.search_page = SearchPage()
        self.ranking_page = RankingPage()
        self.user = None

    def search(self, keyword, limit=None, type=None, dimension=None, mode=None, popularity=None):
        """
        Search in pixiv using parameters

        keyword: string to search
        type: manga | illust | ugoira | default any
        dimension: vertical | horizontal | square | default any
        mode: strict_tag | loose | default tag contains
        popularity: a number, add after search keyword as: number users入り | default date descending
        page: which page of the search results to crawl | default 1

        return a PixivResult object
        """
        ids = self.search_page.get_ids(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, limit=limit)
        folder = settings.SEARCH_RESULTS_FOLDER.format(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, limit=limit)
        results = PixivResult(util.generate_artworks_from_ids(ids), folder)
        return results

    def rank(self, mode='daily', max_page=None, date=None, content=None):
        """
        Get ranking in pixiv according to parameters

        mode: daily | weekly | monthly | rookie | original | male | female | default daily
        max_page: 1 page = 50 artworks | default all pages
        date: up to which date | default today, format: yyyymmdd
        content: illust | manga | ugoria | default any

        return a PixivResult object
        """
        ids = self.ranking_page.rank(mode=mode, max_page=max_page, date=date, content=content)
        results = PixivResult(util.generate_artworks_from_ids(ids))
        results.folder = '#PixivRanking-{mode}-{max_page}-{date}-{content}'.format(mode=mode, max_page=max_page, date=date, content=content)
        return results

    def download(self, pixiv_result=None, pixiv_id=None, user_id=None, folder=""):
        """
        Take a PixivResult object and download its content

        folder: folder path to save the downloads

        does not return anything
        """
        if pixiv_result:
            download(pixiv_result, folder)
        if pixiv_id:
            Artwork(pixiv_id).download(folder=folder)


    def login(self, username, password):
        """
        Take username and password attempt to login pixiv

        return a user object
        """
        return User(username=username, password=password)


class User:
    url = 'https://www.pixiv.net/bookmark.php?'
    def __init__(self, username, password):
        self.session = LoginPage().login(username=username, password=password)
        err_msg = 'Failed getting data from user:' + str(username)
        res = util.req(type='get', session=self.session, url=self.url, err_msg=err_msg)
        if res:
            res = re.search(r'class="user-name"title="(.*?)"', res.text)
            self.username = res.group(1) if res else username
        else:
            self.username = username

    def _get_my_favorites_ids(self, params):
        ids = []
        curr_page = 0
        while True:
            curr_page += 1
            if curr_page != 1:
                params['p'] = curr_page
            res = util.req(type='get', session=self.session, url=self.url, params=params)
            if res:
                ids_found = re.findall('(\d{8})_p0', res.text)
                if len(ids_found) == 0:
                    util.log('0 id found in this page, reached end')
                    break
                else:
                    ids += ids_found
                    if len(ids) != len(set(ids)):
                        util.log('We found duplicates in the favs, which likely to indicate failure while retrieve correct items...', type='inform save')
                        util.log('url:', self.url, 'params:', params, type='inform save')
            time.sleep(1)
        return ids

    def favs(self, type=None, limit=None):
        """
        type: public | private | default both
        """
        params = dict()
        if type:
            if type == 'public':
                params['rest'] = 'show'
            elif type == 'private':
                params['rest'] = 'hide'
            else:
                raise ValueError('Invalid type:', str(type))
            ids = self._get_my_favorites_ids(params=params)
        else:
            params['rest'] = 'show'
            public_ids = self._get_my_favorites_ids(params=params)
            params['rest'] = 'hide'
            private_ids = self._get_my_favorites_ids(params=params)
            ids = public_ids + private_ids
        results = PixivResult(util.generate_artworks_from_ids(ids, limit=limit))
        results.folder = settings.FAV_DOWNLOAD_FOLDER.format(username=self.username)
        return results

    def access(self, pixiv_id, type=None):
        return OtherUser(pixiv_id=pixiv_id, session=self.session)


class download:

    def download_list_of_items(self, items, results_dict):
        for item in items:
            item.download(folder=self.folder, results_dict=results_dict)

    def __init__(self, pixiv_result, folder):
        results_dict = self._download_initilizer(pixiv_result, folder)
        start_time = time.time()
        util.multiprocessing_(items=pixiv_result.artworks, small_list_executor=self.download_list_of_items, results_dict=results_dict)
        end_time = time.time()
        self._log_download_results(pixiv_result, start_time, end_time, folder, results_dict)

    def _download_initilizer(self, pixiv_result, folder):
        if not folder:
            folder = pixiv_result.folder
        self.folder = folder
        self.folder = util.clean(self.folder) # remove not allowed chracters as file name in windows
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        results_dict = Manager().dict()
        results_dict['total_expected'] = len(pixiv_result.artworks)
        results_dict['success'] = 0
        results_dict['failed'] = 0
        results_dict['skipped'] = 0
        return results_dict

    def _log_download_results(self, pixiv_result, start_time, end_time, folder="", results_dict=dict()):
        if not folder:
            folder = pixiv_result.folder
        folder = util.clean(folder)
        if not os.path.exists(folder):
            os.mkdir(folder)
        util.log('', end=settings.CLEAR_LINE, type='inform') # remove last printed saved ok line
        util.log('', type='inform') # move to next line
        for key, value in results_dict.items():
            util.log(key.title(), ':', value, type='inform save')
        util.log('Time Taken:', str(end_time - start_time) + 's', type='inform save')
        util.log('Done', str(results_dict['success'] + results_dict['skipped'])  + '/' + str(results_dict['total_expected']) ,'=>', folder, type='inform save')
