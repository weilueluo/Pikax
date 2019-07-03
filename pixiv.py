# -*- coding: utf-8 -*-

import requests, time, itertools
import re, sys, os
from util import log
import multiprocessing
from multiprocessing import Pool as ThreadPool
from pages import LoginPage, SearchPage
from items import Artwork, SearchResult

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

    def generate_artworks_from_ids(self, ids):
        start = time.time()
        log('Generating Artwork objects ... ')
        pool = ThreadPool(8)
        artworks = []
        try:
            artworks = pool.imap_unordered(Artwork.factory, ids)
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

        results = SearchResult(self.generate_artworks_from_ids(ids))
        results.folder = '#{keyword}-{type}-{dimension}-{mode}-{popularity}-{max_page}'.format(keyword=keyword, type=type, dimension=dimension, mode=mode, popularity=popularity, max_page=max_page)
        return results


    def download(self, data, folder=""):
        start = time.time()
        log('Starting downloads...')
        if not folder:
            folder = data.folder
        if not os.path.exists(folder):
            os.mkdir(folder)
        folders = itertools.repeat(folder)
        pool = ThreadPool(16)
        try:
            res = pool.map(Artwork.downloader, zip(data.artworks, folders))
        except multiprocessing.ProcessError as e:
            pool.terminate()
            log('Error:', str(e))
        finally:
            pool.close()
            pool.join()
            log('done.', len(data.artworks), 'artworks in', str(time.time() - start) + 's =>', str(folder))
