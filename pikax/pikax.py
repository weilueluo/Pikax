# -*- coding: utf-8 -*-
"""Contain classes for use

**Classes**
:class: Pikax
"""

import time, re, sys, os, json
from multiprocessing import Manager

from . import util, settings
from .pages import SearchPage, RankingPage
from .items import Artwork, PixivResult, User
from .exceptions import LoginError, ReqException

sys.stdout.reconfigure(encoding='utf-8')

__all__ = ['Pikax']

class Pikax:
    """Representing Pixiv.net

    **Functions**
    :func search: returns a PixivResult Object
    :func rank: returns a PixivResult Object
    :func download: download artworks given PixivResult and folder as str
    :func login: returns a User Object given username and password

    """
    def __init__(self):
        self.search_page = SearchPage()
        self.ranking_page = RankingPage()
        self.user = None

    def search(self, keyword, limit=None, type=None, dimension=None, mode=None, popularity=None):
        """Search Pixiv and returns PixivResult Object

        **Description**
        Invoke search method in SearchPage and create a PixivResult Object using default folder in settings

        **Returns**
        :return: result of the search in SearchPage with default search folder as in settings.py
        :rtype: PixivResult Object
        """
        util.log('Searching:', keyword)

        artworks = self.search_page.search(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, limit=limit)
        folder = settings.SEARCH_RESULTS_FOLDER.format(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, limit=limit)
        results = PixivResult(artworks, folder)

        return results

    def rank(self, mode='daily', limit=None, date=None, content=None):
        """Rank Pixiv and returns PixivResult Object

        **Description**
        Invoke rank method in RankingPage and create a PixivResult Object using default folder in settings

        **Returns**
        :return: result of the rank in RankingPage with default rank folder as in settings.py
        :rtype: PixivResult Object
        """
        util.log('Ranking:', mode)

        artworks = self.ranking_page.rank(mode=mode, limit=limit, date=date, content=content)
        folder = settings.RANK_RESULTS_FOLDER.format(mode=mode, limit=limit, date=date, content=content)
        results = PixivResult(artworks, folder)
        return results

    # PixivResult > user_id > artwork_id
    def download(self, pixiv_result=None, artwork_id=None, user_id=None, folder=""):
        """Download the given pixiv_result or artwork_id with given folder

        **Description**
        download the given PixivResult Object or artwork_id
        if PixivResult is given, artwork_id is ignored

        **Parameters**
        :param pixiv_result:
            the PixivResult Object which contains artworks to download
        :type pixiv_result:
            PixivResult or None

        :param artwork_id:
            the artwork id of the artwork to download
        :type artwork_id:
            str or None

        :param folder:
            the folder used to save the download result, default folder in settings.py
            is used if not given
        :type folder:
            str or None

        **Returns**
        :return: None
        :rtype: None

        """

        util.log('Downloading ... ', start='\r\n', inform=True)

        if pixiv_result:
            download(pixiv_result, folder)
        elif user_id:
            pass
        elif artwork_id:
            try:
                Artwork(artwork_id).download(folder=folder)
                util.log('', inform=True) # move to next line
            except ArtworkError as e:
                util.log(str(e), error=True, save=True)

    def login(self, username, password):
        """Return the logined User Object

        **Description**
        returns the User Object build from given username and password

        **returns**
        :return: a logged User
        :rtype: User

        """
        util.log('Login:', username)
        return User(username=username, password=password)

    # def access(self, pixiv_id):
    #     util.log('access:', pixiv_id)
    #     return User(pixiv_id=pixiv_id)



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
        util.log('', end=settings.CLEAR_LINE, inform=True) # remove last printed saved ok line
        util.log('', inform=True) # move to next line
        for key, value in results_dict.items():
            util.log(key.title(), ':', value, inform=True, save=True)
        util.log('Time Taken:', str(end_time - start_time) + 's', inform=True, save=True)
        util.log('Done', str(results_dict['success'] + results_dict['skipped'])  + '/' + str(results_dict['total_expected']) ,'=>', folder, inform=True, save=True)
