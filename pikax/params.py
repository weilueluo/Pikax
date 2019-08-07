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


# type
ILLUST = Type.ILLUST
NOVEL = Type.NOVEL
USER = Type.USER
MANGA = Type.MANGA

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


def get_a_month_timedelta():
    today = datetime.date.today()
    a_month_in_days = calendar.monthrange(year=today.year, month=today.month)[1]
    return datetime.timedelta(days=a_month_in_days)


def get_a_year_timedelta():
    today = datetime.date.today()
    a_year_in_days = 365 + calendar.isleap(today.year)
    return datetime.timedelta(days=a_year_in_days)


# search range
A_DAY = datetime.timedelta(days=1)
A_WEEK = datetime.timedelta(days=7)
A_MONTH = get_a_month_timedelta()
A_YEAR = get_a_year_timedelta()


# collections params, e.g. illusts, novels
class Collections:
    class Restrict(PikaxEnum):
        PUBLIC = 'public'
        PRIVATE = 'private'


PUBLIC = Collections.Restrict.PUBLIC
PRIVATE = Collections.Restrict.PRIVATE

# for testing
def main():
    assert Search.Type.is_valid(DATE_DESC) is False
    assert Search.Type.is_valid(DATE_ASC) is False
    assert Search.Type.is_valid(ANY) is False
    assert Search.Type.is_valid(EXACT) is False
    assert Search.Type.is_valid(PARTIAL) is False
    assert Search.Type.is_valid(TEXT) is False
    assert Search.Type.is_valid(KEYWORD) is False
    assert Search.Type.is_valid(ILLUST)
    assert Search.Type.is_valid(NOVEL)
    assert Search.Type.is_valid(USER)


if __name__ == '__main__':
    main()
