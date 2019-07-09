# -*- coding: utf-8 -*-
import traceback
import re, os, time, util, threading, settings, json
from pages import LoginPage
from exceptions import ReqException, ArtworkError, UserError

__all__ = ['Artwork', 'PixivResult']


# raise ArtworkError if failed to init
class Artwork():
    referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    ajax_url = 'https://www.pixiv.net/ajax/illust/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    # https://www.pixiv.net/touch/ajax/illust/details?illust_id=75637165
    """
    self.id
    self.original_url
    self.views
    self.bookmarks
    self.likes
    self.comments
    self.title
    self.author
    """

    def __init__(self, id):
        self.id = str(id)
        ajax_url = self.ajax_url + self.id
        try:
            respond = util.req(type='get', url=ajax_url, log_req=False)
            image_data = util.json_loads(respond.content)
            # self.data = dict()
            self.original_url = image_data['body']['urls']['original']
            self.views = image_data['body']['viewCount']
            self.bookmarks = image_data['body']['bookmarkCount']
            self.likes = image_data['body']['likeCount']
            self.comments = image_data['body']['commentCount']
            self.title = image_data['body']['illustTitle']
            self.author = image_data['body']['userName']
            res = re.search(r'/([\d]+_.*)', self.original_url)
            if res != None:
                self.file_name = str(self.author) + '_' + res.group(1)
            else:
                util.log('Cannot find file name of artwork id', self.id, type='save inform')
                self.file_name = 'unknown_' + self.original_url
        except ReqException as e:
            # util.log(str(e), type='error save')
            traceback.print_exc()
            raise ArtworkError('Failed to init artwork from id: ' + str(self.id))

    # def __getattr__(self, key):
    #     try:
    #         return self.data[key]
    #     except KeyError:
    #         raise AttributeError(key)

    # for multiprocessing, return None if failed to init artwork
    def factory(id):
        try:
            return Artwork(id)
        except ArtworkError as e:
            util.log(str(e), type='error save')
            return None

    def download(self, folder="", results_dict=None):
        pic_detail = '[' + str(self.title) + '] by [' + str(self.author) + ']'
        self.file_name = util.clean_filename(self.file_name)
        if folder:
            self.file_name = util.clean_filename(folder) + '/' + self.file_name
        if os.path.isfile(self.file_name):
            if results_dict:
                results_dict['skipped'] += 1
            util.log(pic_detail, 'skipped, reason:', self.file_name, 'exists')
            return
        # pixiv check will check referer
        self.headers['referer'] = self.referer_url + self.id
        try:
            err_msg = pic_detail + ' Failed'
            original_pic_respond = util.req(type='get', url=self.original_url, headers=self.headers, err_msg=err_msg, log_req=False)
            with open(self.file_name, 'wb') as file:
                file.write(original_pic_respond.content)
                util.log(pic_detail + ' OK', type='inform', start=settings.CLEAR_LINE, end='\r')
            if results_dict:
                results_dict['success'] += 1
        except ReqException as e:
            util.log(str(e), type='error save')
            util.log(pic_detail + ' FAILED', type='inform save', start=settings.CLEAR_LINE)
            if results_dict:
                results_dict['failed'] += 1

class PixivResult:
    """
    - iterable
    self.artworks
    self.folder
    """
    def __init__(self, artworks, folder=""):
        self.artworks = artworks
        count = 0
        if folder:
            self.folder = folder
        else:
            while True:
                self.folder = '#PixivResult' + str(count)
                count += 1
                if not os.path.exists(self.folder):
                    break

    def __getitem__(self, index):
        return self.artworks[index]

    def __len__(self):
        return len(self.artworks)

# raise LoginError if failed to login
class User:

    """
    self.id
    self.account
    self.name
    self.create_time
    self.location
    self.country
    self.birth
    self.age
    self.follows
    self.background
    self.title
    self.description
    self.pixiv_url

    self.illusts
    self.mangas

    """

    # for retrieving details
    _user_details_url = 'https://www.pixiv.net/touch/ajax/user/details?' # param id
    _self_details_url = 'https://www.pixiv.net/touch/ajax/user/self/status' # need login session

    # for retrieving contents
    _content_url = 'https://www.pixiv.net/touch/ajax/user/illusts?'
    _bookmarks_url = 'https://www.pixiv.net/touch/ajax/user/bookmarks?'

    def _get_bookmark_artworks(self):
        params = dict()
        params['id'] = self.id
        curr_page = 0
        last_page = 1 # a number not equal to curr_page
        bookmark_ids = []
        try:
            while curr_page < last_page:
                curr_page += 1
                params['p'] = curr_page
                res = util.req(url=self._bookmarks_url, params=params)
                res_json = util.json_loads(res.content)
                bookmark_ids += [illust['id'] for illust in res_json['bookmarks']]
                last_page = res_json['lastPage']
        except (ReqException, json.JSONDecodeError, KeyError) as e:
            util.log(str(e), type='error')
            util.log('Failed to get bookmarks from id:', self.id)

        bookmarks = util.generate_artworks_from_ids(bookmark_ids)
        return bookmarks


    def _get_content_artworks(self, type):
        params = dict()
        params['id'] = self.id
        params['type'] = type
        curr_page = 0
        last_page = 1 # a number not equal to curr_page
        items_ids = []

        try:
            while curr_page < last_page:
                curr_page += 1
                params['p'] = curr_page
                res = util.req(url=self._content_url, params=params)
                res_json = util.json_loads(res.content)
                items_ids += [illust['id'] for illust in res_json['illusts']]
                last_page = res_json['lastPage']
        except (ReqException, json.JSONDecodeError, KeyError) as e:
            util.log(str(e), type='error')
            util.log('Failed to get ' + type + ' from id:', self.id)

        artworks = util.generate_artworks_from_ids(items_ids)
        return artworks



    def __init__(self, username=None, password=None, pixiv_id=None):

        # check input
        if not (username and password or pixiv_id):
            raise UserError('Please supply username and password or pixiv id')

        # login session
        self.session = None
        self.details = dict()

        # find pixiv id from username and password
        if username and password:
            try:
                self.session = LoginPage().login(username=username, password=password)
                status_data = util.req(session=self.session, url=self._self_details_url)
                status_data_json = util.json_loads(status_data.text)
                pixiv_id = status_data_json['body']['user_status']['user_id']
            except ReqException as e:
                util.log(str(e), type='error save')
                raise UserError('Failed to load user data')

        # get information from pixiv id
        if pixiv_id:
            self.data = dict()
            try:
                params = dict({'id': pixiv_id})
                data = util.req(url=self._user_details_url, params=params)
                data_json = util.json_loads(data.text)
            except (ReqException, json.JSONDecodeError) as e:
                util.log(str(e), type='error')
                raise UserError('Failed to load user data')

        # save user information
        data_json = data_json['user_details']
        self.id = data_json['user_id']
        self.account = data_json['user_account']
        self.name = data_json['user_name']
        self.create_time = data_json['user_create_time']
        self.location = data_json['location']
        self.country = data_json['user_country']
        self.birth = data_json['user_birth']
        self.age = data_json['user_age']
        self.follows = data_json['follows']
        self.background = data_json['bg_url']
        self.title = data_json['meta']['title']
        self.description = data_json['meta']['description']
        self.pixiv_url = data_json['meta']['canonical']

        # init user's contents
        self.illusts = []
        self.mangas = []
        self.bookmarks = []
        self.has_illusts = data_json['has_illusts']
        self.has_mangas = data_json['has_mangas']
        # self.has_novels = data_json['has_novels']
        self.has_bookmarks = data_json['has_bookmarks']

        # now get items of the user

        if self.has_illusts:
            self.illusts = self._get_content_artworks(type='illusts')
            util.log('Added', len(self.illusts), 'illustrations')

        if self.has_mangas:
            self.mangas = self._get_content_artworks(type='manga')
            util.log('Added', len(self.mangas), 'mangas')

        if self.has_bookmarks and self.session:
            self.bookmarks = self._get_bookmark_artworks()
            util.log('Added', len(self.bookmarks), 'bookmarks')
