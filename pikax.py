# -*- coding: utf-8 -*-

import time, util
import re, sys, os, settings, json
from multiprocessing import Manager
from pages import SearchPage, RankingPage
from items import Artwork, PixivResult, User
from exceptions import LoginError, ReqException

sys.stdout.reconfigure(encoding='utf-8')

__all__ = ['Pixiv']

class Pixiv:

    def __init__(self):
        self.search_page = SearchPage()
        self.ranking_page = RankingPage()
        self.user = None

    def search(self, keyword, limit=None, type=None, dimension=None, mode=None, popularity=None):
        util.log('Searching:', keyword)

        artworks = self.search_page.search(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, limit=limit)
        folder = settings.SEARCH_RESULTS_FOLDER.format(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, limit=limit)
        results = PixivResult(artworks, folder)

        return results

    def rank(self, mode='daily', limit=None, date=None, content=None):
        util.log('Ranking:', mode)

        artworks = self.ranking_page.rank(mode=mode, limit=limit, date=date, content=content)
        folder = settings.RANK_RESULTS_FOLDER.format(mode=mode, limit=limit, date=date, content=content)
        results = PixivResult(artworks, folder)
        return results

    # PixivResult > user_id > artwork_id
    def download(self, pixiv_result=None, artwork_id=None, user_id=None, folder=""):
        util.log('Downloading ... ', start='\r\n', type='inform')

        if pixiv_result:
            download(pixiv_result, folder)
        elif user_id:
            pass
        elif artwork_id:
            try:
                Artwork(artwork_id).download(folder=folder)
                util.log('', type='inform') # move to next line
            except ArtworkError as e:
                util.log(str(e), type='error')

    def login(self, username, password):
        """
        Take username and password attempt to login pixiv

        return a User object
        """
        util.log('Login:', username)
        return User(username=username, password=password)

    def access(self, pixiv_id):
        util.log('access:', pixiv_id)
        return User(pixiv_id=pixiv_id)


# def _get_my_favorites_ids(self, params):
#     ids = []
#     curr_page = 0
#     exception_count = 0
#     while True:
#         curr_page += 1
#         if curr_page != 1:
#             params['p'] = curr_page
#
#         try:
#             res = util.req(type='get', session=self.session, url=self.url, params=params)
#         except ReqException as e:
#             util.log(str(e), type='error save')
#             exception_count += 1
#             if exception_count > settings.MAX_WHILE_TRUE_LOOP_EXCEPTIONS:
#                 util.log('Too many exceptions encountered:', exception_count, 'terminating ... ', type='inform save')
#                 break
#             else:
#                 continue
#
#         ids_found = re.findall('(\d{8})_p\d', res.text)
#         if len(ids_found) == 0:
#             util.log('0 id found in this page, reached end')
#             break
#         else:
#             ids += ids_found
#             if len(ids) != len(set(ids)):
#                 util.log('We found duplicates in the favs, which likely to indicate failure while retrieve correct items...', type='inform save')
#                 util.log('url:', self.url, 'params:', params, type='inform save')
#         time.sleep(1) # dont req too fasts
#     return ids
#
# # raise ValueError if type is invalid
# def favs(self, type=None, limit=None):
#     """
#     type: public | private | default both
#     """
#     params = dict()
#     if type:
#         if type == 'public':
#             params['rest'] = 'show'
#         elif type == 'private':
#             params['rest'] = 'hide'
#         else:
#             raise ValueError('Invalid type:', str(type))
#         ids = self._get_my_favorites_ids(params=params)
#     else:
#         params['rest'] = 'show'
#         public_ids = self._get_my_favorites_ids(params=params)
#         params['rest'] = 'hide'
#         private_ids = self._get_my_favorites_ids(params=params)
#         ids = public_ids + private_ids
#     results = PixivResult(util.generate_artworks_from_ids(ids, limit=limit))
#     results.folder = settings.FAV_DOWNLOAD_FOLDER.format(username=self.username)
#     return results
#
# def access(self, pixiv_id, type=None):
#     return OtherUser(pixiv_id=pixiv_id, session=self.session)


class download:

    def download_list_of_items(self, items, results_dict):
        for item in items:
            item.download(folder=self.folder, results_dict=results_dict)

    def __init__(self, pixiv_result, folder):
        results_dict = self._download_initilizer(pixiv_result, folder)
        start_time = time.time()
        util.multiprocessing_(items=pixiv_result.artworks, small_list_executor=self.download_list_of_items, results_saver=results_dict)
        end_time = time.time()
        self._log_download_results(pixiv_result, start_time, end_time, folder, results_dict)

    def _download_initilizer(self, pixiv_result, folder):
        if not folder:
            folder = pixiv_result.folder
        self.folder = folder
        self.folder = util.clean_filename(self.folder) # remove not allowed chracters as file name in windows
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
        folder = util.clean_filename(folder)
        if not os.path.exists(folder):
            os.mkdir(folder)
        util.log('', end=settings.CLEAR_LINE, type='inform') # remove last printed saved ok line
        util.log('', type='inform') # move to next line
        for key, value in results_dict.items():
            util.log(key.title(), ':', value, type='inform save')
        util.log('Time Taken:', str(end_time - start_time) + 's', type='inform save')
        util.log('Done', str(results_dict['success'] + results_dict['skipped'])  + '/' + str(results_dict['total_expected']) ,'=>', folder, type='inform save')
