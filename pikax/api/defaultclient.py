import datetime
import re
import time
from typing import List, Union

from .models import APIPagesInterface, APIUserInterface, APIAccessInterface
from .. import params, settings
from .. import util
from ..exceptions import ReqException, SearchError, RankError, UserError


__all__ = ['DefaultAPIClient', 'DefaultAPIUser']


class DefaultIllustSearch:
    """Representing the search page in pixiv.net

    **Functions**
    :func search: Used to search in pixiv.net

    """
    _search_popularity_postfix = u'users入り'

    def __init__(self):
        pass

    @classmethod
    def _set_params(cls, search_type, dimension, match, sort, search_range):

        search_params = dict()
        if search_type:  # default match all rank_type
            if not params.SearchType.is_valid(search_type):
                search_params['rank_type'] = search_type.value

        if dimension:  # default match all ratios
            if params.Dimension.is_valid(dimension):
                search_params['ratio'] = dimension.value
            else:
                raise SearchError(f'dimension rank_type: {dimension} is not rank_type of {params.Dimension}')

        if match:  # default match if contain tags
            if not params.Match.is_valid(match):
                raise SearchError(f'match: {match} is not rank_type of {params.Match}')

            if match is params.Match.PARTIAL:  # this is default
                pass
            elif match is params.Match.EXACT:  # specified tags only
                search_params['s_mode'] = 's_tag_full'
            elif match == params.Match.ANY:
                search_params['s_mode'] = 's_tc'

        if sort:
            if not params.Sort.is_valid(sort):
                raise SearchError(f'sort: {sort} is not rank_type of {params.Sort}')

            if sort is params.Sort.DATE_DESC:
                search_params['order'] = 'date_d'
            elif sort is params.Sort.DATE_ASC:
                search_params['order'] = 'date'

        if search_range:
            if params.Range.is_valid(search_range):
                search_range = search_range.value
            if isinstance(search_range, datetime.timedelta):
                today = datetime.date.today()
                search_params['ecd'] = str(today)
                search_params['scd'] = str(today - search_range)
            else:
                raise SearchError(f'Invalid range rank_type: {search_range}')

        return search_params

    @classmethod
    def _search_all_popularities_in_list(cls, search_params, keyword, limit, session):
        ids = []
        total_limit = limit
        for popularity in settings.SEARCH_POPULARITY_LIST:
            ids += cls._search(search_params=search_params, keyword=keyword, limit=limit, popularity=popularity,
                               session=session)
            if total_limit:
                num_of_ids_sofar = len(ids)
                if num_of_ids_sofar > total_limit:
                    ids = util.trim_to_limit(ids, total_limit)
                    break
                else:
                    limit = total_limit - num_of_ids_sofar
        return ids

    @classmethod
    def search(cls, keyword, limit=None, search_type=None, dimension=None, match=None, popularity=None, sort=None,
               search_range=None, session=None):
        """Used to search in pixiv.net

        **Parameters**
        :param session:
        :param search_range:
        :param sort:
        :param keyword:
            a space separated of tags, used for search
        :rank_type keyword:
             str

        :param limit:
            number of artworks is trimmed to this number if too many, may not be enough
        :rank_type limit:
             int or None(default)

        :param search_type:
            rank_type of artworks,
            'illust' | 'manga', default any
        :rank_type search_type:
             str or None(default)

        :param dimension:
            dimension of the artworks, 'vertical' | 'horizontal' | 'square', default any
        :rank_type dimension:
             str or None(default)

        :param match:
            define the way of matching artworks with a artwork,
            'strict_tag' matches when any keyword is same as a tag in the artwork
            'loose' matches when any keyword appears in title, description or tags of the artwork
            default matches when any keyword is part of a tag of the artwork
        :rank_type match:
             str or None(default)

        :param popularity:
            this is based on a pixiv search trick to return popular results for non-premium users,
            eg, pixiv automatically adds a 1000users入り tag when a artwork has 1000 likes
            when popularity is given, the str ' ' + popularity + 'users入り' is added to keyword string,
            common popularity of 100, 500, 1000, 5000, 10000, 20000 is strongly suggested, since pixiv does
            not add tag for random likes such as 342users入り
            when str 'popular' is given, it will search for all results with users入り tag in
            [20000, 10000, 5000, 1000, 500]
            note that 'popular' is the only string accepted
        :rank_type popularity:
            int or str or None(default)

        **Returns**
        :return: a list of Artwork Object
        :rtype: python list


        **Raises**
        :raises SearchError: if invalid order, mode or dimension is given


        **See Also**
        :class: items.Artwork

        """

        # for recording
        start = time.time()

        # setting parameters
        search_params = cls._set_params(search_type=search_type, dimension=dimension, match=match, sort=sort,
                                        search_range=search_range)

        if not keyword:
            keyword = ''

        # search starts
        if popularity == 'popular':
            ids = cls._search_all_popularities_in_list(search_params=search_params, keyword=keyword, limit=limit,
                                                       session=session)
        else:
            ids = cls._search(search_params=search_params, keyword=keyword, limit=limit, popularity=popularity,
                              session=session)

        # log ids found
        util.log('Found', str(len(ids)), 'ids for', keyword, 'in', str(time.time() - start) + 's')

        return ids
        # # build artworks from ids
        # artworks = util.generate_artworks_from_ids(ids)
        #
        # return artworks

    @classmethod
    def _search(cls, search_params, keyword, popularity, limit, session):
        curr_page = 1
        ids_so_far = []
        url = 'https://www.pixiv.net/search.php?'
        search_regex = r'(\d{8})_p\d'
        while True:
            # get a page's ids
            search_params['p'] = curr_page
            search_params['word'] = str(keyword)
            if popularity is not None:
                search_params['word'] += ' ' + str(popularity) + cls._search_popularity_postfix
            util.log('Searching illust id for params:', search_params, 'at page:', curr_page)
            try:
                err_msg = 'Failed getting ids from params ' + str(search_params) + ' page: ' + str(curr_page)
                results = util.req(url=url, params=search_params, session=session,
                                   err_msg=err_msg, log_req=False)
            except ReqException as e:
                util.log(str(e), error=True, save=True)
                if curr_page == 1:
                    util.log('Theres no result found for input', inform=True, save=True)
                else:
                    util.log('End of search at page: ' + str(curr_page), inform=True, save=True)
                return ids_so_far

            ids = re.findall(search_regex, results.text)

            # set length of old ids and new ids,
            # use later to check if reached end of all pages
            old_len = len(ids_so_far)
            ids_so_far += ids
            ids_so_far = list(set(ids_so_far))
            new_len = len(ids_so_far)

            # if limit is specified, check if reached limited number of items
            if limit is not None:
                if limit == new_len:
                    return ids_so_far
                elif limit < new_len:
                    return util.trim_to_limit(ids_so_far, limit=limit)
                # limit has not reached

            # now check if any new items is added
            if old_len == new_len:  # if no new item added, end of search pages
                if limit is not None:  # if limit is specified, it means search ended without meeting user's limit
                    util.log('Search did not return enough items for limit:', new_len, '<', limit, inform=True,
                             save=True)
                return ids_so_far

            # search next page
            curr_page += 1


class DefaultRank:
    """Representing ranking page in pixiv.net

        **Functions**
        :func rank: used to get artworks in rank page in pixiv.net

        """

    url = 'https://www.pixiv.net/ranking.php?'

    def __init__(self):
        pass

    @classmethod
    def _check_inputs(cls, content, rank_type):
        if content is params.Content.ILLUST:
            allowed = [params.RankType.DAILY, params.RankType.MONTHLY, params.RankType.WEEKLY, params.RankType.ROOKIE]
            if rank_type not in allowed:
                raise RankError('Illust content is only available for rank_type in', allowed)

    @classmethod
    def _set_params(cls, content, date, rank_type):
        rank_params = dict()

        rank_params['format'] = 'json'

        if rank_type:
            if params.RankType.is_valid(rank_type):
                rank_params['mode'] = rank_type.value
            else:
                raise RankError(f'rank rank_type: {rank_type} is not rank_type of {params.RankType}')

        if content:
            if params.Content.is_valid(content):
                rank_params['content'] = content.value
            else:
                raise RankError(f'content: {content} is not rank_type of {params.Content}')

        if date:
            if isinstance(date, str):
                rank_params['date'] = date
            elif isinstance(date, datetime.date):
                rank_params['date'] = format(date, '%Y%m%d')
            elif isinstance(date, params.Date):
                rank_params['date'] = format(date.value, '%Y%m%d')
            else:
                raise RankError(f'Invalid date: {date}')

        if rank_params['date'] == format(datetime.date.today(), '%Y%m%d'):
            del rank_params['date']  # pixiv always shows previous day rank for today

        return rank_params

    @classmethod
    def _rank(cls, rank_params, limit):
        ids = []
        page_num = 0
        while True:
            page_num += 1
            rank_params['p'] = page_num
            try:
                res = util.req(url=cls.url, params=rank_params).json()
            except ReqException as e:
                util.log(str(e), error=True, save=True)
                util.log('End of rank at page:', page_num, inform=True, save=True)
                break
            if 'error' in res:
                util.log('End of page while searching', str(rank_params) + '. Finished')
                break
            else:
                ids += [content['illust_id'] for content in res['contents']]

            # check if number of ids reached requirement
            if limit:
                num_of_ids_found = len(ids)
                if limit == num_of_ids_found:
                    break
                elif limit < num_of_ids_found:
                    ids = util.trim_to_limit(ids, limit)
                    break

        return ids

    @classmethod
    def rank(cls, rank_type, content, limit=None, date=None):
        """Used to get artworks from pixiv ranking page

        **Parameters**
        :param rank_type:
            rank_type of ranking as in pixiv.net,
            'daily' | 'weekly' | 'monthly' | 'rookie' | 'original' | 'male' | 'female', default daily
        :rank_type rank_type:
            params.Rank

        :param limit:
            number of artworks to return, may not be enough, default all
        :rank_type limit:
            int or None

        :param date:
            the date when ranking occur,
            if string given it must be in 'yyyymmdd' format
            eg. given '20190423' and mode daily will return the daily ranking of pixiv on 2019 April 23
            eg. given '20190312' and mode monthly will return the monthly ranking from 2019 Feb 12 to 2019 March 12
            default today
        :rank_type date:
            Datetime or str or None

        :param content:
            rank_type of artwork to return,
            'illust' | 'manga', default 'illust'
        :rank_type content:
            params.Content

        **Returns**
        :return: a list of artworks
        :rtype: list

        """

        # some combinations are not allowed
        cls._check_inputs(content=content, rank_type=rank_type)

        # set paramters
        rank_params = cls._set_params(content=content, date=date, rank_type=rank_type)

        # rank starts
        ids = cls._rank(rank_params=rank_params, limit=limit)

        # if limit is specified, check if met
        if limit:
            num_of_ids_found = len(ids)
            if num_of_ids_found < limit:
                util.log('Items found in ranking is less than requirement:', num_of_ids_found, '<', limit, inform=True)

        return ids


class DefaultAPIUser(APIUserInterface):
    # for retrieving details
    _user_details_url = 'https://www.pixiv.net/touch/ajax/user/details?'  # param id
    _self_details_url = 'https://www.pixiv.net/touch/ajax/user/self/status'  # need login session

    # for retrieving contents
    _content_url = 'https://www.pixiv.net/touch/ajax/user/illusts?'
    _bookmarks_url = 'https://www.pixiv.net/touch/ajax/user/bookmarks?'
    _illusts_url = 'https://www.pixiv.net/touch/ajax/illust/user_illusts?user_id={user_id}'

    _profile_url = 'https://www.pixiv.net/ajax/user/{user_id}/profile/all'

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

    def __init__(self, user_id, session=None):
        self._id = user_id
        self._session = session
        self._config()

    def _config(self):
        # get information from user id
        details_params = dict({'id': self.id})
        try:
            data = util.req(url=self._user_details_url, params=details_params, session=self._session).json()
        except ReqException as e:
            util.log(str(e), error=True, save=True)
            raise UserError('Failed to load user information')
        # save user information, not used yet, for filter in the future
        data = data['body']['user_details']
        self._id = data['user_id']
        self._account = data['user_account']
        self._name = data['user_name']
        self.title = data['meta']['title']
        self.description = data['meta']['description']
        self.follows = data['follows']

        # init user's contents
        try:
            data = util.req(url=self._profile_url.format(user_id=self.id), session=self._session).json()
            self._illust_ids = list(data['body']['illusts'].keys()) if data['body']['illusts'] else []
            self._manga_ids = list(data['body']['manga'].keys()) if data['body']['manga'] else []
        except (ReqException, KeyError) as e:
            util.log(str(e), error=True, save=True)
            raise UserError(f'Failed to load user creations: {e}')

    def illusts(self, limit=None):
        """Returns illustrations uploaded by this user

        **Parameters**
        :param limit:
            limit the amount of illustrations found, if exceed
        :rank_type limit:
            int or None

        :return: the results of attempting to retrieve this user's uploaded illustrations
        :rtype: PixivResult Object

        """
        return util.trim_to_limit(self._illust_ids, limit=limit)

    def mangas(self, limit=None):
        """Returns mangas uploaded by this user

        **Parameters**
        :param limit:
            limit the amount of mangas found, if exceed
        :rank_type limit:
            int or None

        :return: the results of attempting to retrieve this user's uploaded mangas
        :rtype: PixivResult Object

        """
        return util.trim_to_limit(self._manga_ids, limit=limit)

    def bookmarks(self, limit: int = None, bookmark_type: params.Type = params.Type.ILLUST,
                  restrict: params.Restrict = params.Restrict.PUBLIC) -> List[int]:
        raise NotImplementedError('Bookmark is inaccessible without logging into Pixiv')

    @property
    def account(self):
        return self._account

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id


class DefaultAPIClient(APIPagesInterface, APIUserInterface, APIAccessInterface):

    def __init__(self, session=None):
        self._session = session

    def search(self, keyword: str = '', search_type: params.SearchType = params.SearchType.ILLUST_OR_MANGA,
               match: params.Match = params.Match.PARTIAL, sort: params.Sort = params.Sort.DATE_DESC,
               search_range: Union[datetime.timedelta, params.Range] = None, limit: int = None) -> List[int]:
        if search_type is params.SearchType.ILLUST_OR_MANGA:
            return DefaultIllustSearch.search(keyword=keyword, search_type=search_type, match=match, sort=sort,
                                              search_range=search_range, limit=limit, session=self._session)

    def rank(self, limit: int = None, date: Union[str, datetime.date] = format(datetime.date.today(), '%Y%m%d'),
             content: params.Content = params.Content.ILLUST, rank_type: params.RankType = params.RankType.DAILY) -> \
            List[int]:
        return DefaultRank.rank(limit=limit, date=date, content=content, rank_type=rank_type)

    def visits(self, user_id: int) -> APIUserInterface:
        return DefaultAPIUser(user_id=user_id, session=self._session)

    def bookmarks(self, limit: int = None, bookmark_type: params.Type = params.Type.ILLUST,
                  restrict: params.Restrict = params.Restrict.PUBLIC) -> List[int]:
        raise NotImplementedError('Bookmark is inaccessible in Pixiv without login')

    def illusts(self, limit: int = None) -> List[int]:
        raise NotImplementedError('Illust is inaccessible in Pixiv without login')

    def mangas(self, limit: int = None) -> List[int]:
        raise NotImplementedError('Manga is inaccessible in Pixiv without login')

    @property
    def account(self):
        raise NotImplementedError('Account is inaccessible in Pixiv without login')

    @property
    def id(self):
        raise NotImplementedError('Id is inaccessible in Pixiv without login')

    @property
    def name(self):
        raise NotImplementedError('Name is inaccessible in Pixiv without login')


def test():
    user = DefaultAPIUser(user_id=9665193)
    client = DefaultAPIClient()
    ids = user.illusts(limit=15)
    assert len(ids) == 15, len(ids)

    ids = user.mangas(limit=1)
    assert len(ids) == 0 or len(ids) == 1, len(ids)
    ids = client.search(keyword='arknights', limit=234, sort=params.Sort.DATE_DESC,
                        search_type=params.SearchType.ILLUST_OR_MANGA,
                        match=params.Match.EXACT,
                        search_range=params.Range.A_MONTH)
    assert len(ids) == 234, len(ids)

    ids = client.rank(rank_type=params.RankType.DAILY, limit=400, date=datetime.date.today(),
                      content=params.Content.ILLUST)
    assert len(ids) == 400, len(ids)

    user_id = 38088
    user = client.visits(user_id=user_id)
    print('id', user.id)
    print('account', user.account)
    print('name', user.name)
    user_illust_ids = user.illusts(limit=65)
    assert len(user_illust_ids) == 65, len(user_illust_ids)

    user_manga_ids = user.mangas(limit=2)
    assert len(user_manga_ids) == 2

    print('Successfully tested default client')


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    test()


if __name__ == '__main__':
    main()
