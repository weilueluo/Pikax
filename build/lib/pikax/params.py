import calendar
import datetime
import enum


class PikaxEnum(enum.Enum):
    @classmethod
    def is_valid(cls, value):
        return isinstance(value, cls)


class Type(PikaxEnum):
    ILLUST = 'illust'
    USER = 'user'
    MANGA = 'manga'

    _member_to_container_map = {
        'illust': 'illusts',
        'user': 'user_previews',
        'manga': 'illusts',  # intended
    }

    @classmethod
    def get_response_container_name(cls, key):
        return cls._member_to_container_map.value[key]


class Match(PikaxEnum):
    # illusts and novel match
    EXACT = 'exact_match_for_tags'
    PARTIAL = 'partial_match_for_tags'
    # illusts only
    ANY = 'title_and_caption'


class Sort(PikaxEnum):
    DATE_DESC = 'date_desc'
    DATE_ASC = 'date_asc'


class RankType(PikaxEnum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    ROOKIE = 'rookie'


class Dimension(PikaxEnum):
    HORIZONTAL = '0.5'
    VERTICAL = '-0.5'
    SQUARE = '0'


class Range(PikaxEnum):
    A_DAY = datetime.timedelta(days=1)
    A_WEEK = datetime.timedelta(days=7)
    A_MONTH = datetime.timedelta(
        days=calendar.monthrange(year=datetime.date.today().year, month=datetime.date.today().month)[1])
    A_YEAR = datetime.timedelta(days=365 + calendar.isleap(datetime.date.today().year))


class Date(PikaxEnum):
    TODAY = format(datetime.date.today(), '%Y%m%d')


# collections params, e.g. illusts, novels
class Restrict(PikaxEnum):
    PUBLIC = 'public'
    PRIVATE = 'private'


class CreationType(PikaxEnum):
    ILLUST = 'illust'
    MANGA = 'manga'


class DownloadType(PikaxEnum):
    ILLUST = enum.auto()
    MANGA = enum.auto()


class ProcessType(PikaxEnum):
    ILLUST = 'illust'
    MANGA = 'manga'

    _process_to_download_map = {
        ILLUST: DownloadType.ILLUST,
        MANGA: DownloadType.MANGA
    }

    @classmethod
    def map_process_to_download(cls, process_type):
        if cls.is_valid(process_type):
            return cls._process_to_download_map.value[process_type.value]
        else:
            raise KeyError(f'process type: {process_type} is not type of {ProcessType}')


class SearchType(PikaxEnum):
    ILLUST_OR_MANGA = 'illust'
    # USER = 'user'  # XXX: Need implementation

    _search_to_process_map = {
        ILLUST_OR_MANGA: ProcessType.ILLUST
    }

    @classmethod
    def map_search_to_process(cls, search_type):
        if cls.is_valid(search_type):
            return cls._search_to_process_map.value[search_type.value]
        else:
            raise KeyError(f'search type: {search_type} is not type of {SearchType}')


class Content(PikaxEnum):
    ILLUST = 'illust'
    MANGA = 'manga'

    _content_to_process_map = {
        ILLUST: ProcessType.ILLUST,
        MANGA: ProcessType.MANGA
    }

    @classmethod
    def map_content_to_process(cls, content_type):
        if cls.is_valid(content_type):
            return cls._content_to_process_map.value[content_type.value]
        else:
            raise KeyError(f'content type: {content_type} is not type of {Content}')


class BookmarkType(PikaxEnum):
    ILLUST_OR_MANGA = 'illust'

    _bookmark_to_process_map = {
        'illust': ProcessType.ILLUST
    }

    _bookmark_to_download_map = {
        'illust': DownloadType.ILLUST
    }

    @classmethod
    def map_bookmark_to_process(cls, bookmark_type):
        if cls.is_valid(bookmark_type):
            return cls._bookmark_to_process_map.value[bookmark_type.value]
        else:
            raise KeyError(f'bookmark type: {bookmark_type} is not type of {cls}')

    @classmethod
    def map_bookmark_to_download(cls, bookmark_type):
        if cls.is_valid(bookmark_type):
            return cls._bookmark_to_download_map.value[bookmark_type.value]
        else:
            raise KeyError(f'bookmark type: {bookmark_type} is not type of {cls}')


# for testing
def main():
    assert Type.is_valid(Date.DATE_DESC) is False
    assert Type.is_valid(Date.DATE_ASC) is False
    assert Type.is_valid(Match.ANY) is False
    assert Type.is_valid(Match.EXACT) is False
    assert Type.is_valid(Match.PARTIAL) is False
    assert Type.is_valid(Match.TEXT) is False
    assert Type.is_valid(Match.KEYWORD) is False
    assert Type.is_valid(Type.ILLUST)
    assert Type.is_valid(Type.NOVEL)
    assert Type.is_valid(Type.USER)


if __name__ == '__main__':
    main()
