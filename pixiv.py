# -*- coding: utf-8 -*-

import requests, time, itertools
import re, sys, os, math
from util import log
import multiprocessing
from multiprocessing import Pool as ThreadPool
from pages import SearchPage, RankingPage
from items import Artwork, PixivResult

sys.stdout.reconfigure(encoding='utf-8')

class Pixiv:
    headers = {
        'referer': 'https://www.pixiv.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    def __init__(self):
        # self.login_page = LoginPage()
        # self.session = self.login_page.login(username, password)
        self.search_page = SearchPage()
        self.ranking_page = RankingPage()

    def get_chunksize(self, total_size):
        div = math.sqrt(total_size)
        return int(total_size / (total_size / div))

    def generate_artworks_from_ids(self, ids):
        start = time.time()
        log('Generating Artwork objects ... ')
        pool = ThreadPool(multiprocessing.cpu_count() * 2)
        artworks = []
        num_of_ids = len(ids)
        chunksize = self.get_chunksize(num_of_ids)
        try:
            artworks = pool.imap_unordered(Artwork.factory, ids, chunksize=chunksize)
        except multiprocessing.ProcessError as e:
            pool.terminate()
            log('Error:', str(e))
        finally:
            pool.close()
            pool.join()
            log('Done. Tried', len(ids), 'artworks objects in' ,str(time.time() - start) + 's')

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
        log('Starting downloads...')
        if not folder:
            folder = data.folder
        if not os.path.exists(folder):
            os.mkdir(folder)
        folders = itertools.repeat(folder)
        pool = ThreadPool(multiprocessing.cpu_count() * 2)
        num_of_artworks = len(data.artworks)
        chunksize = self.get_chunksize(num_of_artworks)
        try:
            res = pool.imap_unordered(Artwork.downloader, zip(data.artworks, folders), chunksize=chunksize)
        except multiprocessing.ProcessError as e:
            pool.terminate()
            log('Error:', str(e))
        finally:
            pool.close()
            pool.join()
            log('done.', len(data.artworks), 'artworks in', str(time.time() - start) + 's =>', str(folder))
