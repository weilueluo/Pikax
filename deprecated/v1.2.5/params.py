import calendar
import enum
import datetime


class PikaxEnum(enum.Enum):
    @classmethod
    def is_valid(cls, value):
        return isinstance(value, cls)


##
# search
##

class Type(PikaxEnum):
    ILLUST = 'illust'
    NOVEL = 'novel'
    USER = 'user'
    MANGA = 'manga'
    GIF = 'NOTSET'

    NOVELS = 'novels'  # used internally by client class

    _member_to_container_map = {
        'illust': 'illusts',
        'novel': 'novels',
        'user': 'user_previews',
        'manga': 'illusts',  # intended
        'novels': 'novels',
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
    # novel only
    TEXT = 'text'
    KEYWORD = 'keyword'


class Sort(PikaxEnum):
    DATE_DESC = 'date_desc'
    DATE_ASC = 'date_asc'


class Rank(PikaxEnum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    ROOKIE = 'rookie'


class Dimension(PikaxEnum):
    HORIZONTAL = '0.5'
    VERTICAL = '-0.5'
    SQUARE = '0'


class Content(PikaxEnum):
    ILLUST = 'illust'
    MANGA = 'manga'


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
    NOVEL = 'novels'


class BookmarkType(PikaxEnum):
    ILLUST_OR_MANGA = 'illust'
    NOVEL = 'novel'


class SearchType(PikaxEnum):
    ILLUST_OR_MANGA = 'illust'
    NOVEL = 'novel'
    USER = 'user'  # XXX: Need implementation


class ProcessType(PikaxEnum):
    ILLUST = enum.auto()
    MANGA = enum.auto()
    NOVEL = enum.auto()
    GIF = enum.auto()


class DownloadType(PikaxEnum):
    ILLUST = enum.auto()
    MANGA = enum.auto()
    NOVEL = enum.auto()
    GIF = enum.auto()  # XXX need implementation


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
