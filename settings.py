


"""
default headers for sending requests
not all requests uses this headers
"""
DEFAULT_HEADERS = {
    'referer': 'https://www.pixiv.net/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}


"""
default time out in seconds for requests
"""
TIMEOUT = 10

MAX_RETRIES_FOR_REQUEST = 3

"""
LOG_TYPE
'inform': print successive stage and error only
'std': allow print
'save': save error to LOG_FILE only
'inform save' or 'informsave': will do both inform and save only
'': log nothing

'inform' will overwrite 'std'
"""
LOG_TYPE = 'inform std'


"""
file used to log error if save is included in LOG_TYPE
"""
LOG_FILE = 'log.txt'


"""
Folder format for downloading favorites
"""
FAV_DOWNLOAD_FOLDER = '#{username}\'s favs'
# below used in other user only
USER_MANGAS_DOWNLOAD_FOLDER = '#{title}\'s  mangas'
USER_ILLUSTS_DOWNLOAD_FOLDER = '#{title}\'s illusts'
USER_BOOKMARKS_DOWNLOAD_FOLDER = '#{title}\'s bookmarks'
SEARCH_RESULTS_FOLDER = '#PixivSearch_{keyword}_{type}_{dimension}_{mode}_{popularity}_{limit}'
RANK_RESULTS_FOLDER = '#PixivRanking-{mode}-{limit}-{date}-{content}'

"""
String to clear previous stdout line
"""
CLEAR_LINE = '\r' + ' ' * 100 + '\r'


"""

"""
MAX_THREAD_PER_PROCESS = 4

MIN_ITEMS_PER_THREAD = 10


MAX_WHILE_TRUE_LOOP_EXCEPTIONS = 5





"""
user name and password used
"""
username = 'restorecyclebin@gmail.com'
password = '123456'
