# -*- coding: utf-8 -*-

"""
This module contains items for general use

:class: Artwork
:class: PixivResult
:class: User
"""
import re, os, time, threading, json

from . import settings, util
from .pages import LoginPage
from .exceptions import ReqException, ArtworkError, UserError

__all__ = ['Artwork', 'PixivResult', 'User']


# raise ArtworkError if failed to init
class Artwork:
    """Representing a artwork in Pixiv.net

    **Functions**
    :func factory: used for multiprocessing, return None if failed to create
    :func download: used to download this artwork

    **Instance Variables**
    - self.id # int
    - self.views # int
    - self.bookmarks # int
    - self.likes # int
    - self.comments # int

    - self.original_url # str
    - self.title # str
    - self.author # str

    **Raises**
    :raises ArtworkError: if failed to init
    """

    _referer_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    _ajax_url = 'https://www.pixiv.net/ajax/illust/'
    _headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    # https://www.pixiv.net/touch/ajax/illust/details?illust_id=75637165

    def __init__(self, id):
        self.id = id
        _ajax_url = self._ajax_url + str(self.id)
        try:
            respond = util.req(type='get', url=_ajax_url, log_req=False)
            image_data = util.json_loads(respond.content)
            image_data = image_data['body']
            self.original_url = image_data['urls']['original']
            self.views = image_data['viewCount']
            self.bookmarks = image_data['bookmarkCount']
            self.likes = image_data['likeCount']
            self.comments = image_data['commentCount']
            self.title = image_data['illustTitle']
            self.author = image_data['userName']
            self.page_count = image_data['pageCount']
            self.original_url = re.sub(r'(?<=_p)\d', '{page_num}', self.original_url)
        except ReqException as e:
            util.log(str(e), error=True, save=True)
            raise ArtworkError('Artwork id:', str(self.id), 'has been deleted or does not exists')

    # for multiprocessing, return None if failed to init artwork
    def factory(id):
        """return a Artwork Object given its id, None if failed

        **Returns**
        :return: Artwork of that id
        :rtype: Artwork
        """
        try:
            return Artwork(id)
        except ArtworkError as e:
            util.log(str(e), error=True, save=True)
            return None

    def download(self, folder=None, results_dict=None):
        """Download this Artwork Object

        **Description**
        Download this artwork given folder or default folder as in settings.py,
        results_dict is from multiprocessing.Manager used to store download statistics if given
        this will download all pages of the artwork

        **Parameters**
        :param folder:
            Folder to store the download item, default folder in settings.py is used if not given
        :type folder:
            str

        :param results_dict:
            the dict used to store statistic for download, from multiprocessing.Manager
        :type results_dict:
            python dict or None

        **Returns**
        :return: None
        :rtype: None

        """
        # pixiv check will check referer
        self._headers['referer'] = self._referer_url + str(self.id)
        curr_page = 0
        success = True
        skipped = False
        while curr_page < self.page_count:  # start from 0 to page_count - 1
            if settings.MAX_PAGES_PER_ARTWORK:
                if curr_page >= settings.MAX_PAGES_PER_ARTWORK:
                    break
            pic_detail = '[' + str(self.title) + '] p' + str(curr_page) + ' by [' + str(self.author) + ']'
            url = self.original_url.format(page_num=curr_page)
            file_name_search = re.search(r'(\d{8}_p\d.*)', url)
            file_name = file_name_search.group(1) if file_name_search else url
            file_name = util.clean_filename(self.author) + '_' + util.clean_filename(file_name)
            if folder is not None:
                file_name = util.clean_filename(folder) + '/' + file_name

            if os.path.isfile(file_name):
                util.log(pic_detail, 'skipped.', 'Reason:', file_name, 'already exists or access not granted')
                skipped = True
                curr_page += 1
                continue

            try:
                err_msg = pic_detail + ' Failed'
                original_pic_respond = util.req(type='get', url=url, headers=self._headers, err_msg=err_msg,
                                                log_req=False)
                with open(file_name, 'wb') as file:
                    file.write(original_pic_respond.content)
                    util.log(pic_detail + ' OK', inform=True, start=settings.CLEAR_LINE, end='\r')
            except ReqException as e:
                util.log(str(e), error=True, save=True)
                util.log(pic_detail + ' FAILED', inform=True, save=True, start=settings.CLEAR_LINE)
                success = False

            curr_page += 1

        # log result
        if results_dict:
            if skipped:
                results_dict['skipped'] += 1
            elif success:
                results_dict['success'] += 1
            else:
                results_dict['failed'] += 1

            results_dict['total pages'] += self.page_count


class PixivResult:
    """Encapsulate results of actions; interface for download

    **Description**
    this class is used to store artworks and folder as string,
    designed to pass to Pikax.download, and it is iterable

    **Instance Variables**
    - self.artworks # list
    - self.folder # str

    # Instances below are meant to used with filter
    # currently == != <= >= < > are supported, returns a new PixivResult
    - self.id # int
    - self.views # int
    - self.bookmarks # int
    - self.likes # int
    - self.comments # int

    **Functions**
    :func __add__: `a + b` returns a new PixivResult contains unique artworks from `a` and `b`
    :func __sub__: `a - b` returns a new PixivResult contains artworks from `a` but not `b`

    """

    def __init__(self, artworks, folder=""):
        self.artworks = list(artworks)
        # generate unique folder if not given
        if folder:
            self.folder = folder
        else:
            count = 0
            while True:
                self.folder = '#PixivResult[' + str(count) + ']'
                count += 1
                if not os.path.exists(self.folder):
                    break

        # they are meant to compare with a number and return a new PixivResult object
        self.likes = self._ComparableItem(self, 'likes')
        self.comments = self._ComparableItem(self, 'comments')
        self.views = self._ComparableItem(self, 'views')
        self.id = self._ComparableItem(self, 'id')
        self.bookmarks = self._ComparableItem(self, 'bookmarks')

    def __getitem__(self, index):
        return self.artworks[index]

    def __len__(self):
        return len(self.artworks)

    def __add__(self, other):

        self_len = len(self.artworks)
        other_len = len(other.artworks)
        artworks = list(set(self.artworks + other.artworks))
        new_len = len(artworks)

        folder = util.clean_filename(str(self.folder) + '+' + str(other.folder))
        result = PixivResult(artworks, folder)

        util.log('Added {self_len} + {other_len} => {sum}'.format(self_len=self_len, other_len=other_len, sum=new_len),
                 start='\r\n', inform=True)

        return result

    def __sub__(self, other):

        self_len = len(self.artworks)
        other_len = len(other.artworks)
        artworks = list(item for item in self.artworks if item not in other.artworks)
        new_len = len(artworks)

        folder = util.clean_filename(str(self.folder) + '-' + str(other.folder))
        result = PixivResult(artworks, folder)

        util.log('Subbed {self_len} - {other_len} => {sum}'.format(self_len=self_len, other_len=other_len, sum=new_len),
                 start='\r\n', inform=True)

        return result

    class _ComparableItem:

        def __init__(self, outer_instance, name):
            self.name = name
            self.outer_instance = outer_instance

        def __eq__(self, value):
            util.log('Filtering {name} == {value}'.format(name=self.name, value=value), start='\r\n', inform=True)

            old_len = len(self.outer_instance.artworks)
            artworks = list(filter(lambda item: getattr(item, self.name) == value, self.outer_instance.artworks))
            new_len = len(artworks)

            folder = util.clean_filename(str(self.outer_instance.folder) + 'eq' + str(value))
            result = PixivResult(artworks, folder)

            util.log('done {} => {}'.format(old_len, new_len), inform=True)

            return result

        def __ne__(self, value):
            util.log('Filtering {name} != {value}'.format(name=self.name, value=value), start='\r\n', inform=True)

            old_len = len(self.outer_instance.artworks)
            artworks = list(filter(lambda item: getattr(item, self.name) != value, self.outer_instance.artworks))
            new_len = len(artworks)

            folder = util.clean_filename(str(self.outer_instance.folder) + 'ne' + str(value))
            result = PixivResult(artworks, folder)

            util.log('done {} => {}'.format(old_len, new_len), inform=True)

            return result

        def __lt__(self, value):
            util.log('Filtering {name} < {value}'.format(name=self.name, value=value), start='\r\n', inform=True)

            old_len = len(self.outer_instance.artworks)
            artworks = list(filter(lambda item: getattr(item, self.name) < value, self.outer_instance.artworks))
            new_len = len(artworks)

            folder = util.clean_filename(str(self.outer_instance.folder) + 'lt' + str(value))
            result = PixivResult(artworks, folder)

            util.log('done {} => {}'.format(old_len, new_len), inform=True)

            return result

        def __le__(self, value):
            util.log('Filtering {name} <= {value}'.format(name=self.name, value=value), start='\r\n', inform=True)

            old_len = len(self.outer_instance.artworks)
            artworks = list(filter(lambda item: getattr(item, self.name) <= value, self.outer_instance.artworks))
            new_len = len(artworks)

            folder = util.clean_filename(str(self.outer_instance.folder) + 'le' + str(value))
            result = PixivResult(artworks, folder)

            util.log('done {} => {}'.format(old_len, new_len), inform=True)

            return result

        def __gt__(self, value):
            util.log('Filtering {name} > {value}'.format(name=self.name, value=value), start='\r\n', inform=True)

            old_len = len(self.outer_instance.artworks)
            artworks = list(filter(lambda item: getattr(item, self.name) > value, self.outer_instance.artworks))
            new_len = len(artworks)

            folder = util.clean_filename(str(self.outer_instance.folder) + 'gt' + str(value))
            result = PixivResult(artworks, folder)

            util.log('done {} => {}'.format(old_len, new_len), inform=True)

            return result

        def __ge__(self, value):
            util.log('Filtering {name} >= {value}'.format(name=self.name, value=value), start='\r\n', inform=True)

            old_len = len(self.outer_instance.artworks)
            artworks = list(filter(lambda item: getattr(item, self.name) >= value, self.outer_instance.artworks))
            new_len = len(artworks)

            folder = util.clean_filename(str(self.outer_instance.folder) + 'ge' + str(value))
            result = PixivResult(artworks, folder)

            util.log('done {} => {}'.format(old_len, new_len), inform=True)

            return result


# https://github.com/oz123/oz123.github.com/blob/master/media/uploads/readonly_properties.py
def read_only_attrs(*attrs):
    def class_changer(cls):
        class User(cls):
            def __setattr__(self, name, new_value):
                if name not in attrs:
                    pass
                elif name not in self.__dict__:
                    pass
                else:
                    raise AttributeError('This attribute is read only:', name)

                return super().__setattr__(name, new_value)

        return User

    return class_changer


# raise LoginError if failed to login
@read_only_attrs('login', 'id', 'account', 'name', 'follows', 'background_url', 'title', 'description', 'pixiv_url',
                 'has_bookmarks', 'has_illusts', 'has_mangas')
class User:
    """This class represent a user and contains actions which needs login in pixiv.net

    **Description**
    Session will be generate if username and password or a requests.Session object
    is provided. User can be created with user id only but this will cause incomplete
    data to be received and will also receive a warning:
    "User initialized without username and password or session will results in incomplete data"

    **Instance Variables**

    - self.illusts # PixivResult
    - self.mangas # PixivResult
    - self.session # requests.Session

    ### Below are read only
    - self.id # str
    - self.account # string
    - self.name # string
    - self.follows # int
    - self.background_url # string
    - self.title # string
    - self.description # string
    - self.pixiv_url # string
    - self.has_mangas # boolean
    - self.has_bookmarks # boolean
    - self.has_illusts # boolean
    - self.r18
    - self.r18g

    **Functions**
    :func illusts: returns illustrations uploaded by this user
    :func mangas: returns mangas uploaded by this user
    :func bookmarks: returns bookmarks of this user
    :func visits: returns a user which has the same session of this user

    **Raises**
    :raises UserError: if failed to init

    """

    # for retrieving details
    _user_details_url = 'https://www.pixiv.net/touch/ajax/user/details?'  # param id
    _self_details_url = 'https://www.pixiv.net/touch/ajax/user/self/status'  # need login session

    # for retrieving contents
    _content_url = 'https://www.pixiv.net/touch/ajax/user/illusts?'
    _bookmarks_url = 'https://www.pixiv.net/touch/ajax/user/bookmarks?'
    _illusts_url = 'https://www.pixiv.net/touch/ajax/illust/user_illusts?user_id={user_id}'

    # for settings
    _settings_url = 'https://www.pixiv.net/setting_user.php'
    # user language for settings
    _user_lang_dict = {
        'zh': u'保存',
        'zh_tw': u'保存',
        'ja': u'変更',
        'en': u'Update',
        'ko': u'변경'
    }

    def __init__(self, username=None, password=None, user_id=None, session=None):

        # check input
        # must provide either username and password or at least user_id
        if not ((username and password) or user_id):
            raise UserError('Please supply username and password or user id (and session)')

        # if only user id is provided, give incomplete data warning
        if not (username and password or session) and user_id:
            util.log('User initialized without username and password or session may results in incomplete data',
                     warn=True, save=True)

        # login session
        self.session = session

        # for login user
        self._r18 = None
        self._r18g = None
        self._lang = None
        self._login = False

        # find pixiv id from username and password and save r18 & r18g settings
        if username and password:
            try:
                login_page = LoginPage()
                self.session = login_page.login(username=username, password=password)
                status_data = util.req(session=self.session, url=self._self_details_url)
                status_data_json = util.json_loads(status_data.text)
                user_id = status_data_json['body']['user_status']['user_id']
            except ReqException as e:
                util.log(str(e), error=True, save=True)
                raise UserError('Failed to load user id')

            # save user's settings for r18 and r18g
            try:
                res = util.req(url=self._settings_url, session=self.session)
                self._r18 = re.search(r'name="r18" value="show" checked>', res.text) is not None
                self._r18g = re.search(r'name="r18g" value="2" checked>', res.text) is not None
                lang_search_res = re.search(r'option value="(\w\w)" selected>', res.text)
                if lang_search_res:
                    self._lang = lang_search_res.group(1)
                else:
                    raise UserError('Failed to find user language in respond')
            except ReqException as e:
                raise UserError('Failed to retrieve r18/r18g settings')

            # save user token, for changing r18 and r18g
            self._token = self._get_token()
            # if username and password is provided, this is a logined user
            self._login = True

        # if user id is not given and failed to retrieve user id
        if not user_id:
            raise UserError('Failed to get user id')

        # get information from user id
        self.data = dict()
        params = dict({'id': user_id})
        try:
            data = util.req(session=self.session, url=self._user_details_url, params=params)
            data_json = util.json_loads(data.text)
        except (ReqException, json.JSONDecodeError) as e:
            util.log(str(e), error=True, save=True)
            raise UserError('Failed to load user information')

        # save user information, not used yet, for filter in the future
        data_json = data_json['user_details']
        self.id = data_json['user_id']
        self.account = data_json['user_account']
        self.name = data_json['user_name']
        self.title = data_json['meta']['title']
        self.description = data_json['meta']['description']
        self.pixiv_url = data_json['meta']['canonical']
        self.follows = data_json['follows']
        self.background_url = data_json['bg_url']

        # init user's contents
        self.illust_artworks = []
        self.manga_artworks = []
        self.bookmark_artworks = []
        self.has_illusts = data_json['has_illusts'] or False
        self.has_mangas = data_json['has_mangas'] or False
        # self.has_novels = data_json['has_novels']
        self.has_bookmarks = data_json['has_bookmarks'] or False

    def _get_token(self):
        try:
            res = util.req(url=self._settings_url, session=self.session)
            tt_result = re.search(r'name="tt" value="(.*?)"', res.text)
            if tt_result:
                tt = tt_result.group(1)
                util.log('successfully retrieved user token:', tt)
                return tt
            else:
                raise UserError('Failed to find user token in respond')
        except ReqException as e:
            raise UserError('Failed to retrieve user token')

    @property
    def login(self):
        return self._login

    @property
    def lang(self):
        if not self._login:
            raise UserError('Please login before viewing user language')

        return self._lang

    @property
    def r18(self):
        if not self._login:
            raise UserError('Please login before viewing user r18g settings')
        return self._r18

    @r18.setter
    def r18(self, new_r18):
        try:
            self._property_setter(r18=new_r18)
            self._r18 = new_r18
            util.log('r18 =>', self._r18)
        except ReqException as e:
            util.log('Failed to set r18 to', str(new_r18) + ', remained as', self._r18, error=True)

    @property
    def r18g(self):
        if not self._login:
            raise UserError('Please login before viewing user r18g settings')
        return self._r18g

    @r18g.setter
    def r18g(self, new_r18g):
        try:
            self._property_setter(r18g=new_r18g)
            self._r18g = new_r18g
            util.log('r18g =>', self._r18g)
        except ReqException as e:
            util.log('Failed to set r18g to', str(new_r18g) + ', remained as', self._r18g, error=True)

    def _property_setter(self, r18=None, r18g=None):
        # raise ReqException if fails
        # this will change pixiv account's language to english
        # raise user error if not login
        if not self._login:
            raise UserError('Please login before setting r18 & r18 content')

        form = dict()
        form['mode'] = 'mod'
        form['user_language'] = self._lang
        form['submit'] = self._user_lang_dict[self._lang]
        form['tt'] = self._token if self._token else self._get_token()

        if r18g is not None:  # if want to change r18g
            form['r18g'] = '2' if r18g else '1'
        else:
            form['r18g'] = '2' if self._r18g else '1'

        if r18 is not None:  # if want to change r18
            form['r18'] = 'show' if r18 else 'hide'
        else:
            form['r18'] = 'show' if self._r18 else 'hide'

        # submit change request
        util.req(type='post', url=self._settings_url, session=self.session, data=form)

    def _get_bookmark_artworks(self, limit=None):
        params = dict()
        params['id'] = self.id
        curr_page = 0
        last_page = 1  # a number more than curr_page, change later in loop
        bookmark_ids = []
        try:
            while curr_page < last_page:
                curr_page += 1
                params['p'] = curr_page
                res = util.req(session=self.session, url=self._bookmarks_url, params=params)
                res_json = util.json_loads(res.content)
                bookmark_ids += [illust['id'] for illust in res_json['bookmarks']]
                if limit is not None:
                    if len(bookmark_ids) > limit:
                        bookmark_ids = util.trim_to_limit(items=bookmark_ids, limit=limit)
                        break
                last_page = res_json['lastPage']
        except (ReqException, json.JSONDecodeError, KeyError) as e:
            util.log(str(e), error=True)
            util.log('Failed to get bookmarks from id:', self.id)

        bookmarks = util.generate_artworks_from_ids(bookmark_ids)
        return bookmarks

    # for manga only, illust found better ajax url
    def _get_content_artworks(self, type, limit=None):
        params = dict()
        params['id'] = self.id
        params['type'] = type
        curr_page = 0
        last_page = 1  # a number more than curr_page
        items_ids = []

        try:
            while curr_page < last_page:
                curr_page += 1

                params['p'] = curr_page
                res = util.req(session=self.session, url=self._content_url, params=params)
                res_json = util.json_loads(res.content)
                items_ids += [illust['id'] for illust in res_json['illusts']]
                if limit is not None:
                    if len(items_ids) > limit:
                        items_ids = util.trim_to_limit(items=items_ids, limit=limit)
                        break
                last_page = res_json['lastPage']
        except (ReqException, json.JSONDecodeError, KeyError) as e:
            util.log(str(e), error=True)
            util.log('Failed to get ' + type + ' from id:', self.id)

        artworks = util.generate_artworks_from_ids(items_ids)
        return artworks

    def _get_illust_artworks(self, limit=None):
        try:
            res = util.req(session=self.session, url=self._illusts_url.format(user_id=self.id))
            illust_ids = eval(res.text)  # string to list
            artworks = util.generate_artworks_from_ids(illust_ids, limit=limit)
            return artworks
        except ReqException as e:
            util.log(str(e), error=True, save=True)
            util.log('Failed to get illustrations from user id:', self.id)
            return []

    def illusts(self, limit=None):
        """Returns illustrations uploaded by this user

        **Parameters**
        :param limit:
            limit the amount of illustrations found, if exceed
        :type limit:
            int or None

        :return: the results of attempting to retrieve this user's uploaded illustrations
        :rtype: PixivResult Object

        """
        util.log('Getting illustrations from id:', self.id)
        if self.has_illusts:
            self.illust_artworks = self._get_illust_artworks(limit=limit)
        else:
            util.log('User with id:', self.id, 'has no illustrations')
            self.illust_artworks = []

        util.log('Found', len(self.illust_artworks), 'illustrations')
        folder = settings.USER_ILLUSTS_DOWNLOAD_FOLDER.format(title=self.title)
        result = PixivResult(self.illust_artworks, folder=folder)
        return result

    def mangas(self, limit=None):
        """Returns mangas uploaded by this user

        **Parameters**
        :param limit:
            limit the amount of mangas found, if exceed
        :type limit:
            int or None

        :return: the results of attempting to retrieve this user's uploaded mangas
        :rtype: PixivResult Object

        """
        util.log('Getting mangas from id:', self.id)
        if self.has_mangas:
            self.manga_artworks = self._get_content_artworks(type='manga', limit=limit)
        else:
            util.log('User with id:', self.id, 'has no mangas')
            self.manga_artworks = []

        util.log('Found', len(self.manga_artworks), 'mangas')
        folder = settings.USER_MANGAS_DOWNLOAD_FOLDER.format(title=self.title)
        result = PixivResult(self.manga_artworks, folder=folder)
        return result

    def bookmarks(self, limit=None):
        """Returns bookmarks saved by this user

        **Parameters**
        :param limit:
            limit the amount of bookmarks found, if exceed
        :type limit:
            int or None

        :return: the results of attempting to retrieve this user's bookmarks
        :rtype: PixivResult Object

        """
        util.log('Getting bookmarks from id:', self.id)
        if self.has_bookmarks:
            self.bookmark_artworks = self._get_bookmark_artworks(limit=limit)
        else:
            util.log('User with id:', self.id, 'has no bookmarks')
            self.bookmark_artworks = []

        util.log('Found', len(self.bookmark_artworks), 'bookmarks')

        folder = settings.USER_BOOKMARKS_DOWNLOAD_FOLDER.format(title=self.title)
        result = PixivResult(self.bookmark_artworks, folder=folder)
        return result

    def visits(self, user_id):
        """Returns a user build from given user id and this user's session

        **Parameters**
        :param user_id: the user id of the user to visit
        :type user_id: int

        """
        return User(user_id=user_id, session=self.session)
