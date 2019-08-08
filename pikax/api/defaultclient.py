import datetime
import re
import time
from typing import List, Union

from .. import params, settings
from .models import APIPagesInterface, APIUserInterface
from .. import util
from ..exceptions import ReqException, SearchError


class DefaultSearch:
    """Representing the search page in pixiv.net

    **Functions**
    :func search: Used to search in pixiv.net

    """
    _search_url = 'https://www.pixiv.net/search.php?'
    _search_popularity_postfix = u'users入り'
    _search_regex = r'(\d{8})_p\d'

    def __init__(self):
        pass

    @classmethod
    def _set_params(cls, type, dimension, match, sort, range):
        search_params = dict()
        if type:  # default match all type
            if type in [params.Type.ILLUST, params.Type.MANGA]:
                search_params['type'] = type.value
            else:
                raise SearchError(f'Invalid search type: {type}')

        if dimension:  # default match all ratios
            if dimension in [params.Dimension.HORIZONTAL, params.Dimension.VERTICAL, params.Dimension.SQUARE]:
                search_params['ratio'] = dimension.value
            else:
                raise SearchError('Invalid dimension given:', dimension)

        if match:  # default match if contain tags
            if match is params.Match.PARTIAL:  # this is default
                pass
            elif match is params.Match.EXACT:  # specified tags only
                search_params['s_mode'] = 's_tag_full'
            elif match == params.Match.ANY:
                search_params['s_mode'] = 's_tc'
            else:
                raise SearchError(f'Invalid match type given: {match}')

        if sort:
            if sort is params.Sort.DATE_DESC:
                search_params['order'] = 'date_d'
            elif sort is params.Sort.DATE_ASC:
                search_params['order'] = 'date'
            else:
                raise SearchError(f'Invalid sort type: {sort}')

        if range:
            if isinstance(range, datetime.timedelta):
                today = datetime.date.today()
                search_params['ecd'] = str(today)
                search_params['scd'] = str(today - range)
            else:
                raise SearchError(f'Invalid range type: {range}')

        return search_params

    @classmethod
    def _search_all_popularities_in_list(cls, params, keyword, limit):
        ids = []
        total_limit = limit
        for popularity in settings.SEARCH_POPULARITY_LIST:
            ids += cls._search(params=params, keyword=keyword, limit=limit, popularity=popularity)
            if total_limit:
                num_of_ids_sofar = len(ids)
                if num_of_ids_sofar > total_limit:
                    ids = util.trim_to_limit(ids, total_limit)
                    break
                else:
                    limit = total_limit - num_of_ids_sofar
        return ids

    @classmethod
    def search(cls, keyword, limit=None, type=None, dimension=None, match=None, popularity=None, sort=None,
               range=None):
        """Used to search in pixiv.net

        **Parameters**
        :param range:
        :param sort:
        :param keyword:
            a space separated of tags, used for search
        :type keyword:
             str

        :param limit:
            number of artworks is trimmed to this number if too many, may not be enough
        :type limit:
             int or None(default)

        :param type:
            type of artworks,
            'illust' | 'manga', default any
        :type type:
             str or None(default)

        :param dimension:
            dimension of the artworks, 'vertical' | 'horizontal' | 'square', default any
        :type dimension:
             str or None(default)

        :param match:
            define the way of matching artworks with a artwork,
            'strict_tag' matches when any keyword is same as a tag in the artwork
            'loose' matches when any keyword appears in title, description or tags of the artwork
            default matches when any keyword is part of a tag of the artwork
        :type match:
             str or None(default)

        :param popularity:
            this is based on a pixiv search trick to return popular results for non-premium users,
            eg, pixiv automatically adds a 1000users入り tag when a artwork has 1000 likes
            when popularity is given, the str ' ' + popularity + 'users入り' is added to keyword string,
            common popularity of 100, 500, 1000, 5000, 10000, 20000 is strongly suggested, since pixiv does
            not add tag for random likes such as 342users入り
            when str 'popular' is given, it will search for all results with users入り tag in [20000, 10000, 5000, 1000, 500]
            note that 'popular' is the only string accepted
        :type popularity:
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
        search_params = cls._set_params(type=type, dimension=dimension, match=match, sort=sort, range=range)

        if not keyword:
            keyword = ''

        # search starts
        if popularity == 'popular':
            ids = cls._search_all_popularities_in_list(params=search_params, keyword=keyword, limit=limit)
        else:
            ids = cls._search(params=search_params, keyword=keyword, limit=limit, popularity=popularity)

        # log ids found
        util.log('Found', str(len(ids)), 'ids for', keyword, 'in', str(time.time() - start) + 's')

        return ids
        # # build artworks from ids
        # artworks = util.generate_artworks_from_ids(ids)
        #
        # return artworks

    @classmethod
    def _search(cls, params, keyword, popularity, limit):
        curr_page = 1
        ids_so_far = []
        while True:
            # get a page's ids
            params['p'] = curr_page
            params['word'] = str(keyword)
            if popularity is not None:
                params['word'] += ' ' + str(popularity) + cls._search_popularity_postfix
            util.log('Searching id for params:', params, 'at page:', curr_page)
            try:
                err_msg = 'Failed getting ids from params ' + str(params) + ' page: ' + str(curr_page)
                results = util.req(url=cls._search_url, params=params,
                                   err_msg=err_msg, log_req=False)
            except ReqException as e:
                util.log(str(e), error=True, save=True)
                if curr_page == 1:
                    util.log('Theres no result found for input', inform=True, save=True)
                else:
                    util.log('End of search at page: ' + str(curr_page), inform=True, save=True)
                return ids_so_far

            ids = re.findall(cls._search_regex, results.text)

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


class DefaultAPIClient(APIPagesInterface, APIUserInterface):

    def __init__(self):
        pass

    def search(self, keyword: str = '', type: params.Type = params.Type.ILLUST,
               match: params.Match = params.Match.EXACT, sort: params.Sort = params.Sort.DATE_DESC,
               range: datetime.timedelta = None, limit: int = None) -> List[int]:
        return DefaultSearch.search(keyword=keyword, type=type, match=match, sort=sort, range=range, limit=limit)

    def rank(self, limit: int = None, date: Union[str, datetime.datetime] = format(datetime.datetime.today(), '%Y%m%d'),
             type: params.Type = params.Type.ILLUST, rank_type: params.Rank = params.Rank.DAILY) -> List[int]:
        pass

    def bookmarks(self, limit: int) -> List[int]:
        raise NotImplementedError('Default API Client does not implement APIUserInterface')

    def illusts(self, limit: int) -> List[int]:
        raise NotImplementedError('Default API Client does not implement APIUserInterface')

    def novels(self, limit: int) -> List[int]:
        raise NotImplementedError('Default API Client does not implement APIUserInterface')

    def mangas(self, limit: int) -> List[int]:
        raise NotImplementedError('Default API Client does not implement APIUserInterface')


def main():
    client = DefaultAPIClient()
    ids = client.search(keyword='arknights', limit=234, sort=params.DATE_DESC, type=params.ILLUST, match=params.EXACT,
                        range=params.A_MONTH)
    print(ids)
    print(len(ids))


if __name__ == '__main__':
    main()
