# -*- coding: utf-8 -*-
"""Contain classes for use

**Classes**
:class: Pikax
"""

import time, re, sys, os, json, datetime, math
from multiprocessing import Manager

from pikax.exceptions import ArtworkError

from . import util, settings
from .pages import SearchPage, RankingPage
from .items import Artwork, PixivResult, User

sys.stdout.reconfigure(encoding='utf-8')

__all__ = ['Pikax']


class Pikax:
    """Representing Pixiv.net

    **Description**
    If it is not log in,


    **Functions**
    :func search: returns a PixivResult Object
    :func rank: returns a PixivResult Object
    :func download: download artworks given PixivResult and folder as str
    :func login: returns a User Object given username and password
    :func access: returns a User Object given user_id and this pikax Object's session

    """

    def __init__(self, user=None):
        self.user = user
        self.search_page = SearchPage(user=user)
        self.ranking_page = RankingPage(user=user)
        self.logged = user != None

    def search(self, keyword, limit=None, type=None, dimension=None, match=None, popularity=None, order=None,
               mode=None):
        """Search Pixiv and returns PixivResult Object

        **Description**
        Invoke search method in SearchPage and create a PixivResult Object using default folder in settings

        **Returns**
        :return: result of the search in SearchPage with default search folder as in settings.py
        :rtype: PixivResult Object
        """
        util.log('Searching:', keyword)

        artworks = self.search_page.search(keyword=keyword, type=type, dimension=dimension, match=match,
                                           popularity=popularity, limit=limit, order=order, mode=mode)

        folder = settings.SEARCH_RESULTS_FOLDER.format(keyword=keyword, type=type, dimension=dimension, mode=mode,
                                                       popularity=popularity, limit=limit)

        results = PixivResult(artworks, folder)

        return results

    def rank(self, mode=None, limit=None, date=None, content=None, type='daily'):
        """Rank Pixiv and returns PixivResult Object

        **Description**
        Invoke rank method in RankingPage and create a PixivResult Object using default folder in settings

        **Returns**
        :return: result of the rank in RankingPage with default rank folder as in settings.py
        :rtype: PixivResult Object
        """
        util.log('Ranking:', mode)

        artworks = self.ranking_page.rank(mode=mode, limit=limit, date=date, content=content, type=type)
        folder = settings.RANK_RESULTS_FOLDER.format(mode=mode, limit=limit, date=date, content=content)
        results = PixivResult(artworks, folder)
        return results

    # PixivResult > artwork_id
    def download(self, pixiv_result=None, artwork_id=None, folder=None):
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
        if pixiv_result is not None:
            return download.download(pixiv_result, folder)
        elif artwork_id:
            try:
                Artwork(artwork_id).download(folder=folder)
                util.log('', inform=True)  # move to next line
            except ArtworkError as e:
                util.log(str(e), error=True, save=True)

    def login(self, username, password):
        """Return the logined User Object

        **Description**
        returns the User Object build from given username and password
        this will alert pixiv's search and rank to be logged and return more complete results as well

        **returns**
        :return: a logged User
        :rtype: User

        """
        util.log('Login:', username)
        self.user = User(username=username, password=password)
        self.search_page = SearchPage(user=self.user)
        self.ranking_page = RankingPage(user=self.user)
        util.log('Pixiv is now logged in as [{username}]'.format(username=username), inform=True, save=True)
        self.logged = True
        return self.user

    def access(self, user_id):
        """Given a pixiv user id and returns a User Object

        """
        util.log('access:', user_id, 'with user:', self.user)
        return User(user_id=user_id, session=self.user.session if self.user else None)


#
# for download stuff below
#

class download:

    @staticmethod
    def _download_list_of_items(items, results_dict):
        for item in items:
            item.download(folder=results_dict['folder'], results_dict=results_dict)

    @staticmethod
    def _sort_by_pages_count(item):
        if settings.MAX_PAGES_PER_ARTWORK:
            if item.page_count > settings.MAX_PAGES_PER_ARTWORK:
                return settings.MAX_PAGES_PER_ARTWORK
        return item.page_count

    @staticmethod
    def _rearrange_into_optimal_chunks(items, next=True):

        num_of_items = len(items)
        num_of_slots = os.cpu_count()
        while num_of_slots > 1:
            num_of_items_per_slot = math.ceil(num_of_items / num_of_slots)
            if num_of_items_per_slot < settings.MIN_ITEMS_PER_THREAD:
                num_of_slots -= 1
            else:
                break

        if num_of_slots > num_of_items:
            num_of_slots = num_of_items

        slots = []
        for i in range(0, num_of_slots):
            slots.append([])

        # descending page count
        items.sort(key=download._sort_by_pages_count, reverse=True)
        for index, item in enumerate(items):
            index = index % num_of_slots
            slots[index].append(item)

        final_list = []
        for slot in slots:

            # do it twice, one for process one for threading
            if next:
                slot = download._rearrange_into_optimal_chunks(slot, next=False)
            final_list += slot

        return final_list

    @staticmethod
    def _download_initilizer(pixiv_result, folder):
        if folder is None:
            folder = pixiv_result.folder
        folder = str(folder)
        folder = util.clean_filename(folder)  # remove not allowed chracters as file name in windows
        if not os.path.exists(folder):
            os.mkdir(folder)
        pixiv_result.artworks = download._rearrange_into_optimal_chunks(pixiv_result.artworks)
        results_dict = Manager().dict()
        results_dict['total expected'] = len(pixiv_result.artworks)
        results_dict['success'] = 0
        results_dict['failed'] = 0
        results_dict['skipped'] = 0
        results_dict['total pages'] = 0
        results_dict['folder'] = folder
        return results_dict

    @staticmethod
    def _log_download_results(pixiv_result, start_time, end_time, results_dict=dict()):
        util.log('', end=settings.CLEAR_LINE, inform=True)  # remove last printed saved ok line
        util.log('', inform=True)  # move to next line
        for key, value in results_dict.items():
            util.log(key.title(), ':', value, inform=True, save=True)
        util.log('Time Taken:', str(end_time - start_time) + 's', inform=True, save=True)
        util.log('Done',
                 str(results_dict['success'] + results_dict['skipped']) + '/' + str(results_dict['total expected']),
                 end='\n\n', inform=True, save=True)

    @staticmethod
    def download(pixiv_result, folder):
        results_dict = download._download_initilizer(pixiv_result, folder)
        start_time = time.time()
        util.multiprocessing_(items=pixiv_result.artworks, small_list_executor=download._download_list_of_items,
                              results_saver=results_dict)
        end_time = time.time()
        download._log_download_results(pixiv_result, start_time, end_time, results_dict)
        return results_dict
