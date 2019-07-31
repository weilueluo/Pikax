


"""
default headers for sending requests
not all requests uses this headers
"""
DEFAULT_HEADERS = {
    'referer': 'https://www.pixiv.net/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}


"""
default time out in seconds for requests
"""
TIMEOUT = 10

"""
Number of retries for requesting
"""
MAX_RETRIES_FOR_REQUEST = 3


"""
Proxies used for sending requests,
uses requests, map protocol to scheme,
# https://2.python-requests.org/en/master/user/advanced/
e.g.
proxies = {
  'http': 'http://10.10.1.10:3128',
  'https': 'http://10.10.1.10:1080',
}
"""
REQUEST_PROXIES = {}


"""
LOG_TYPE
'inform': print successive stage and error only
'std': allow print
'save': save error to LOG_FILE only
'inform save' or 'informsave': will do both inform and save only
'': log nothing

'inform' will overwrite 'std'
"""
LOG_TYPE = 'inform std warn'


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
RANK_RESULTS_FOLDER = '#PixivRanking-{mode}-{limit}-{content}-{date}'


"""
String to clear previous stdout line
"""
CLEAR_LINE = '\r' + ' ' * 100 + '\r'


"""
Maximum number of threads to used per process
"""
MAX_THREAD_PER_PROCESS = 4

"""
Minimum items per process, if more than is given
"""
MIN_ITEMS_PER_THREAD = 10


"""
Indicate a failure when theres too much exceptions occured during requesting in the same loop
"""
MAX_WHILE_TRUE_LOOP_EXCEPTIONS = 3


"""
Default request error message,
when error message is not given as param to util.req
"""
DEFAULT_REQUEST_ERROR_MSG = 'Exception while {type}'


"""
A artwork id may have multiple pages,
sometimes is not desire to download all of them,
None means download all pages
"""
MAX_PAGES_PER_ARTWORK = 3


"""
List of popularities to use when 'popular' is pass to search
"""
SEARCH_POPULARITY_LIST = [20000, 10000, 5000, 1000, 500]


"""
user name and password used to login
"""
username = 'restorecyclebin@gmail.com'
password = '123456'
