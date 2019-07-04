# -*- coding: utf-8 -*-

import time, itertools, util
import re, sys, os, math
import multiprocessing
from multiprocessing import Pool as ThreadPool
from pages import SearchPage, RankingPage
from items import Artwork, PixivResult, User

sys.stdout.reconfigure(encoding='utf-8')

class Pixiv:

    def __init__(self):
        self.search_page = SearchPage()
        self.ranking_page = RankingPage()
        self.user = None

    def generate_artworks_from_ids(self, ids):
        start = time.time()
        util.log('Generating Artwork objects ... ')
        pool = ThreadPool(multiprocessing.cpu_count())
        artworks = []
        try:
            artworks = pool.map(Artwork.factory, ids)
        except multiprocessing.ProcessError as e:
            pool.terminate()
            util.log('Error:', str(e))
        finally:
            pool.close()
            pool.join()
            util.log('Done. Tried', len(ids), 'artworks objects in' ,str(time.time() - start) + 's')

        return artworks


        """
        keyword: string to search
        type: manga | illust | ugoira | default any
        dimension: vertical | horizontal | square | default any
        mode: strict_tag | loose | default tag contains
        popularity: a number, add after search keyword as: number users入り | default date descending
        page: which page of the search results to crawl | default 1

        return a list of ArtWork object
        """
    def search(self, keyword, max_page=None, type=None, dimension=None, mode=None, popularity=None):
        ids = self.search_page.get_ids(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, max_page=max_page)
        results = PixivResult(self.generate_artworks_from_ids(ids))
        results.folder = '#PixivSearch-{keyword}-{type}-{dimension}-{mode}-{popularity}-{max_page}'.format(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, max_page=max_page)
        return results

        """
        mode: daily | weekly | monthly | rookie | original | male | female | default daily
        max_page: 1 page = 50 artworks | default all pages
        date: up to which date | default today, format: yyyymmdd
        content: illust | manga | ugoria | default any
        """
    def rank(self, mode='daily', max_page=None, date=None, content=None):
        ids = self.ranking_page.rank(mode=mode, max_page=max_page, date=date, content=content)
        results = PixivResult(self.generate_artworks_from_ids(ids))
        results.folder = '#PixivRanking-{mode}-{max_page}-{date}-{content}'.format(mode=mode, max_page=max_page, date=date, content=content)
        return results


    def download(self, data, folder=""):
        start = time.time()
        util.log('Starting downloads...')
        if not folder:
            folder = data.folder
        if not os.path.exists(folder):
            os.mkdir(folder)
        folders = itertools.repeat(folder)
        pool = ThreadPool(multiprocessing.cpu_count())
        try:
            res = pool.map(Artwork.downloader, zip(data.artworks, folders))
        except multiprocessing.ProcessError as e:
            pool.terminate()
            util.log('Error:', str(e))
        finally:
            pool.close()
            pool.join()
            util.log('done. Tried', len(data.artworks), 'artworks in', str(time.time() - start) + 's =>', str(folder))


    def login(self, username, password):
        self.user = User(username=username, password=password)

    def favorites(self, type=None):
        if self.user == None:
            util.log('Please login first')
            return None
        ids = self.user.get_favorites(type=type)
        results = PixivResult(self.generate_artworks_from_ids(ids))
        results.folder = '#' + self.user.username + ' favorites'
        return results
