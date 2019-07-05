# -*- coding: utf-8 -*-

import time, itertools, util
import re, sys, os, math, settings
import multiprocessing
from multiprocessing import Pool as ThreadPool
from pages import SearchPage, RankingPage, UserPage, LoginPage
from items import Artwork, PixivResult

sys.stdout.reconfigure(encoding='utf-8')

class Pixiv:

    def __init__(self):
        self.search_page = SearchPage()
        self.ranking_page = RankingPage()
        self.user = None

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
    def search(self, keyword, max_page=None, type=None, dimension=None, mode=None, popularity=None):
        ids = self.search_page.get_ids(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, max_page=max_page)
        results = PixivResult(util.generate_artworks_from_ids(ids))
        results.folder = '#PixivSearch-{keyword}-{type}-{dimension}-{mode}-{popularity}-{max_page}'.format(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, max_page=max_page)
        return results

    """
    Get ranking in pixiv according to parameters

    mode: daily | weekly | monthly | rookie | original | male | female | default daily
    max_page: 1 page = 50 artworks | default all pages
    date: up to which date | default today, format: yyyymmdd
    content: illust | manga | ugoria | default any

    return a PixivResult object
    """
    def rank(self, mode='daily', max_page=None, date=None, content=None):
        ids = self.ranking_page.rank(mode=mode, max_page=max_page, date=date, content=content)
        results = PixivResult(util.generate_artworks_from_ids(ids))
        results.folder = '#PixivRanking-{mode}-{max_page}-{date}-{content}'.format(mode=mode, max_page=max_page, date=date, content=content)
        return results

    """
    Take a PixivResult object and download its content

    folder: folder path to save the downloads

    does not return anything
    """
    def download(self, pixiv_result, folder=""):
        start = time.time()
        util.log('Starting downloads...', type='inform')
        if not folder:
            folder = pixiv_result.folder
        if not os.path.exists(folder):
            os.mkdir(folder)
        folders = itertools.repeat(folder)
        pool = ThreadPool(multiprocessing.cpu_count())
        try:
            res = pool.map(Artwork.downloader, zip(pixiv_result.artworks, folders))
        except multiprocessing.ProcessError as e:
            pool.terminate()
            util.log('Error:', str(e), type='save inform')
        finally:
            pool.close()
            pool.join()
            util.log('Done. Tried saving', len(pixiv_result.artworks), 'artworks in', str(time.time() - start) + 's =>', str(folder), type='inform')

    """
    Take username and password attempt to login pixiv

    return a user object
    """
    def login(self, username, password):
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

    def get_my_favorites_ids(self, params):
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

    """
    type: public | private | default both
    """
    def get_my_favorites(self, type=None, limit=None):
        params = dict()
        if type:
            if type == 'public':
                params['rest'] = 'show'
            elif type == 'private':
                params['rest'] = 'hide'
            else:
                raise ValueError('Invalid type:', str(type))
            return self.get_my_favorites(session=self.session, url=self.url, params=params)
        else:
            params['rest'] = 'show'
            public_ids = self.get_my_favorites_ids(params=params)
            params['rest'] = 'hide'
            private_ids = self.get_my_favorites_ids(params=params)
        ids = public_ids + private_ids
        ids = util.trim_to_limit(ids, limit=limit, username=self.username)
        results = PixivResult(util.generate_artworks_from_ids(ids))
        results.folder = settings.FAV_DOWNLOAD_FOLDER.format(username=self.username)
        return results

    def get_others_favorites(self, pixiv_id, limit=None):
        user_page = UserPage(pixiv_id=pixiv_id, session=self.session)
        public_fav_ids = user_page.get_public_fav_ids(limit=limit)
        results = PixivResult(util.generate_artworks_from_ids(public_fav_ids))
        results.folder = settings.FAV_DOWNLOAD_FOLDER.format(username=user_page.username)
        return results

    def access_favs(self, type=None, pixiv_id=None, limit=None):
        if pixiv_id:
            return self.get_others_favorites(pixiv_id=pixiv_id, limit=limit)
        else:
            return self.get_my_favorites(type=type, limit=limit)
