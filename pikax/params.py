import calendar
from enum import Enum
import datetime


class PikaxEnum(Enum):
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
    def get_response_container_name(cls, item):
        if cls.is_valid(item):
            return cls._member_to_container_map.value[item.value]
        else:
            raise KeyError(f'Value {item} does not exists in {cls}')


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


# type
ILLUST = Type.ILLUST
NOVEL = Type.NOVEL
USER = Type.USER
MANGA = Type.MANGA
GIF = Type.GIF

# illusts and novel match
EXACT = Match.EXACT
PARTIAL = Match.PARTIAL

# illusts only
ANY = Match.ANY

# novel match
TEXT = Match.TEXT
KEYWORD = Match.KEYWORD

# search sort
DATE_DESC = Sort.DATE_DESC
DATE_ASC = Sort.DATE_ASC


class Range(PikaxEnum):
    A_DAY = datetime.timedelta(days=1)
    A_WEEK = datetime.timedelta(days=7)
    A_MONTH = datetime.timedelta(
        days=calendar.monthrange(year=datetime.date.today().year, month=datetime.date.today().month)[1])
    A_YEAR = datetime.timedelta(days=365 + calendar.isleap(datetime.date.today().year))


# search range
A_DAY = Range.A_DAY
A_WEEK = Range.A_WEEK
A_MONTH = Range.A_MONTH
A_YEAR = Range.A_YEAR


class Date(PikaxEnum):
    TODAY = format(datetime.date.today(), '%Y%m%d')


# collections params, e.g. illusts, novels
class Collections:
    class Restrict(PikaxEnum):
        PUBLIC = 'public'
        PRIVATE = 'private'


PUBLIC = Collections.Restrict.PUBLIC
PRIVATE = Collections.Restrict.PRIVATE


# for testing
def main():
    assert Type.is_valid(DATE_DESC) is False
    assert Type.is_valid(DATE_ASC) is False
    assert Type.is_valid(ANY) is False
    assert Type.is_valid(EXACT) is False
    assert Type.is_valid(PARTIAL) is False
    assert Type.is_valid(TEXT) is False
    assert Type.is_valid(KEYWORD) is False
    assert Type.is_valid(ILLUST)
    assert Type.is_valid(NOVEL)
    assert Type.is_valid(USER)


if __name__ == '__main__':
    main()
