import calendar
from enum import Enum
import datetime


# search match
ANY = 'title_and_caption'
EXACT = 'exact_match_for_tags'
PARTIAL = 'partial_match_for_tags'

# search sort
DATE_DESC = 'date_desc'
DATE_ASC = 'date_asc'


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
