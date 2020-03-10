import functools
import math
import multiprocessing as mp
import os
import re
import sys
import time

import requests

import pikax
import texts
from pikax import Artwork
from pikax import params
from pikax import settings, PikaxResult, util
from pikax.exceptions import *
from pikax.items import LoginHandler
from importlib import reload


class PikaxHandler:
    def __init__(self):
        self.pikax = pikax.Pikax()
        self.user = None
        self.logged = False

        self.pikax.downloader = Downloader()

    def login(self, username, password):
        status, client = LoginHandler().android_login(username, password)
        if status is LoginHandler.LoginStatus.ANDROID:
            self.pikax.android_client = client
            self.logged = True
        else:
            raise pikax.PikaxException(texts.get('PIKAX_FAILED_LOGIN'))

    def rank(self, rank_type, limit, date, content, folder, pages_limit):
        try:
            if pages_limit:
                old_limit = settings.MAX_PAGES_PER_ARTWORK
                settings.MAX_PAGES_PER_ARTWORK = 1
            result = self.pikax.rank(rank_type=rank_type, limit=limit, date=date, content=content)
            self.pikax.download(result, folder=folder)
            if pages_limit:
                settings.MAX_PAGES_PER_ARTWORK = old_limit
        except PikaxException as e:
            import sys
            sys.stdout.write(texts.get('PIKAX_RANK_FAILED').format(error=e))

    def search(self, keyword, limit, sort, match, popularity, folder, pages_limit):
        try:
            if pages_limit:
                old_limit = settings.MAX_PAGES_PER_ARTWORK
                settings.MAX_PAGES_PER_ARTWORK = 1
            result = self.pikax.search(keyword=keyword, limit=limit, sort=sort, match=match, popularity=popularity)
            self.pikax.download(result, folder)
            if pages_limit:
                settings.MAX_PAGES_PER_ARTWORK = old_limit
        except PikaxException as e:
            import sys
            sys.stdout.write(texts.get('PIKAX_SEARCH_FAILED').format(error=e))

    def download_by_illust_ids(self, illust_ids):
        try:
            artworks, fails = self.pikax.get_id_processor().process(ids=illust_ids,
                                                                    process_type=params.ProcessType.ILLUST)
            result = pikax.DefaultPikaxResult(artworks, download_type=params.DownloadType.ILLUST)
            self.pikax.download(result)
        except pikax.ArtworkError as e:
            sys.stdout.write(texts.get('PIKAX_ILLUST_ID_FAILED').format(error=e))

    def download_by_artist_id(self, artist_id, limit, content, folder, likes, pages_limit):
        try:
            if pages_limit:
                old_limit = settings.MAX_PAGES_PER_ARTWORK
                settings.MAX_PAGES_PER_ARTWORK = 1

            artist = self.pikax.visits(user_id=artist_id)

            content_to_method = {
                params.Content.ILLUST: artist.illusts,
                params.Content.MANGA: artist.mangas
            }
            if not likes:
                limit = None

            try:
                result = content_to_method[content](limit=limit)
            except KeyError:
                # bookmark is not included in the method
                result = artist.bookmarks(limit=limit)

            if likes:
                result = (result.likes > likes).renew_artworks(util.trim_to_limit(result.likes > likes, limit))

            self.pikax.download(result, folder=folder)

            if pages_limit:
                settings.MAX_PAGES_PER_ARTWORK = old_limit

        except PikaxException as e:
            sys.stdout.write(str(e))


class Downloader:

    def __init__(self):
        self.download_type_to_function = {
            params.DownloadType.ILLUST: self.download_illust,
            params.DownloadType.MANGA: self.download_manga,
        }

    @staticmethod
    def download_illust(artwork: Artwork, folder: str = ''):
        artwork_detail = texts.DOWNLOAD_INITIALIZE_FAILED
        folder = str(folder)
        if folder and not os.path.isdir(folder):
            os.mkdir(folder)
        try:
            for status, url_and_headers, filename in artwork:
                url, headers = url_and_headers
                page_num_search = re.search(r'\d{8}_p(\d*)', url)
                page_num = page_num_search.group(1) if page_num_search else -1
                filename = os.path.join(util.clean_filename(str(folder)), util.clean_filename(str(filename)))
                artwork_detail = f'[{str(artwork.title)}] p{page_num} {texts.get("BY")} [{str(artwork.author)}]'
                if status is Artwork.DownloadStatus.OK:

                    if os.path.isfile(filename):
                        yield Artwork.DownloadStatus.SKIPPED, artwork_detail
                        continue

                    with requests.get(url=url, headers=headers) as r:
                        r.raise_for_status()
                        with open(filename, 'wb') as file:
                            for chunk in r.iter_content(chunk_size=1024):
                                file.write(chunk)
                    yield Artwork.DownloadStatus.OK, artwork_detail

                else:
                    yield Artwork.DownloadStatus.FAILED, artwork_detail

        except requests.RequestException as e:
            yield Artwork.DownloadStatus.FAILED, artwork_detail + f': {e}'

    @staticmethod
    def download_manga(artwork: Artwork, folder: str = None):
        return Downloader.download_illust(artwork=artwork, folder=folder)

    @staticmethod
    def download_func(item, target, curr_artwork, curr_page, total_artworks, total_pages, successes, fails,
                      skips):
        download_details = target(item)
        for download_detail in download_details:
            curr_page.value += 1
            status, msg = download_detail
            info = str(msg) + ' ' + str(status.value)
            if status is Artwork.DownloadStatus.OK:
                successes.append(msg)
            elif status is Artwork.DownloadStatus.SKIPPED:
                skips.append(msg)
            else:
                fails.append(msg)
            info = f'{curr_artwork.value} / {total_artworks} ' \
                   f'=> {math.ceil((curr_artwork.value / total_artworks) * 100)}% | ' + info
            util.print_progress(curr_page.value, total_pages, msg=info)
        curr_artwork.value += 1

    def download(self, pikax_result: PikaxResult, folder: str = ''):
        from common import concurrent_download

        if not folder:
            folder = pikax_result.folder

        folder = util.clean_filename(folder)

        if folder and not os.path.isdir(folder):
            os.mkdir(folder)

        download_function = self.download_type_to_function[pikax_result.download_type]
        download_function = functools.partial(download_function, folder=folder)

        artworks = pikax_result.artworks
        total_pages = sum(len(artwork) for artwork in artworks)
        total_artworks = len(artworks)
        manager = mp.Manager()
        curr_artwork = manager.Value('i', 0)
        curr_page = manager.Value('i', 0)
        successes = manager.list()
        fails = manager.list()
        skips = manager.list()

        target = functools.partial(self.download_func,
                                   target=download_function,
                                   curr_artwork=curr_artwork,
                                   curr_page=curr_page,
                                   total_pages=total_pages,
                                   total_artworks=total_artworks,
                                   successes=successes,
                                   fails=fails,
                                   skips=skips,
                                   )

        util.log(texts.get('DOWNLOAD_INITIALIZING').format(total_pages=total_pages, total_artworks=total_artworks),
                 start=os.linesep,
                 inform=True)
        concurrent_download(target=target, items=pikax_result.artworks)
        util.print_done()

        finish_msg = ''
        finish_msg += texts.get('DOWNLOAD_FINISHED_SUCCESS_PAGES').format(successes=len(successes))

        finish_msg += texts.get('DOWNLOAD_FINISHED_SKIPPED_PAGES').format(skips=len(skips))
        for index, skip_info in enumerate(skips):
            finish_msg += texts.get('DOWNLOAD_FINISHED_SKIPPED_INFO').format(counter=index + 1,
                                                                             skip_info=str(skip_info))

        finish_msg += texts.get('DOWNLOAD_FINISHED_FAILED_PAGES').format(fails=len(fails))
        for index, fail_info in enumerate(fails):
            finish_msg += texts.get('DOWNLOAD_FINISHED_FAILED_INFO').format(counter=index + 1, fail_info=str(fail_info))

        download_path = os.path.abspath(folder)
        folder_msg = texts.get('DOWNLOAD_FINISHED_PATH_NOTICE').format(download_path=download_path)
        util.print_done(str(finish_msg + folder_msg))


def trim_to_limit(items, limit):
    if items:
        if limit:
            num_of_items = len(items)

            if num_of_items == limit:
                return items

            if num_of_items > limit:
                items = items[:limit]
                util.log(f'{texts.get("UTIL_TRIMMED")} {num_of_items} {texts.get("UTIL_ITEMS")} '
                         f'=> {limit} {texts.get("UTIL_ITEMS")}')
                # log('Trimmed', num_of_items, 'items =>', limit, 'items')
            else:
                util.log(f'{texts.get("UTIL_TRIM_NUM_ITEMS_LESS_THAN_LIMIT_ERROR")} {num_of_items} < {limit}')
                # log('Number of items are less than limit:', num_of_items, '<', limit, inform=True, save=True)
    return items


pikax.util.trim_to_limit = trim_to_limit


class Printer(object):

    def __init__(self):
        self.is_first_print = True
        self.last_percent = None
        self.last_percent_time_left = None
        self.last_percent_print_time = None
        self.est_time_lefts = [0, 0, 0]
        self.start_time = None
        self.last_printed_line = None

    def print_progress(self, curr, total, title=None, msg=None):
        curr_percent = math.floor(curr / total * 100)
        curr_time = time.time()
        if self.is_first_print:
            est_time_left = float("inf")
            self.is_first_print = False
            self.last_percent_time_left = est_time_left
            self.last_percent_print_time = curr_time
            self.start_time = time.time()
        elif self.last_percent == curr_percent:
            est_time_left = self.last_percent_time_left
        else:
            bad_est_time_left = (curr_time - self.last_percent_print_time) / (curr_percent - self.last_percent) * (
                    100 - curr_percent)
            self.est_time_lefts.append(bad_est_time_left)
            self.est_time_lefts = self.est_time_lefts[1:]
            percent_left = 100 - curr_percent
            percent_diff = curr_percent - self.last_percent
            chunk_left = round(percent_left / percent_diff)
            if chunk_left < len(self.est_time_lefts):
                est_time_left = sum(self.est_time_lefts[-chunk_left:]) / chunk_left if chunk_left != 0 else 0.00
            else:
                est_time_left = sum(self.est_time_lefts) / len(self.est_time_lefts)
            self.last_percent_time_left = est_time_left
            self.last_percent_print_time = curr_time

        self.last_percent = curr_percent

        if est_time_left != 0.0:
            progress_text = '{0} / {1} => {2}% | {3} {4:.2f}{5}'.format(curr, total, curr_percent,
                                                                        texts.get('TIME_LEFT_EST'),
                                                                        est_time_left, texts.get('SECOND'))
        else:
            progress_text = '{0} / {1} => {2}% '.format(curr, total, curr_percent)

        if msg:
            progress_text = progress_text + ' | ' + str(msg)

        progress_text = '\n'.join(progress_text.split('|'))
        if title:
            progress_text = title + '\n\n' + progress_text
        util.log(progress_text, end='', start=settings.CLEAR_LINE, inform=True)
        self.last_printed_line = progress_text

    def print_done(self, msg=None):
        if msg:
            if self.is_first_print:
                util.log(f' [ {texts.get("DONE")} ] => {msg}', normal=True)
            else:
                util.log(' [ {done} ] => {0:.2f}{s} \n{msg}'.format(time.time() - self.start_time, msg=msg,
                                                                    s=texts.get('SECOND'), done=texts.get("DONE")),
                         normal=True)
        else:
            if self.is_first_print:
                util.log(f' [ {texts.get("DONE")} ]', normal=True)
            else:
                util.log(' [ {done} ] => {0:.2f}{s}'.format(time.time() - self.start_time, s=texts.get('SECOND'),
                                                            done=texts.get("DONE")), normal=True)
        self.is_first_print = True
        self.start_time = None
        self.last_percent = None
        self.last_percent_print_time = None
        self.last_percent_time_left = None
        self.last_printed_line = None
        self.est_time_lefts = [0, 0, 0]


def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', inform=False, save=False,
        error=False, warn=False, normal=False):
    import sys
    string = ''.join([start, *objects])
    sys.stdout.write(string)


pikax.util.printer = Printer()

pikax.util.log = log