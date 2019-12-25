"""
default headers for sending requests
not all requests uses this headers
"""
DEFAULT_HEADERS = {
    'referer': 'https://www.pixiv.net/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
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
Minimum waiting time in seconds between two successive requests,
Set this number to a suitable amount to reduce
chances of getting block
"""
DELAY_PER_REQUEST = None

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
'std': allow debug printings
'save': save error to LOG_FILE only
"""
LOG_STD = True
LOG_INFORM = True
LOG_WARN = True
LOG_SAVE = False

"""
file used to log error if save is included in LOG_TYPE
"""
LOG_FILE = 'log.txt'

"""
default folder format for downloading,
do not change, reference only, 
you can specify a new folder when calling pikax.download
"""
DEFAULT_MANGAS_FOLDER = '#{name}\'s  mangas'
DEFAULT_ILLUSTS_FOLDER = '#{name}\'s illusts'
DEFAULT_BOOKMARKS_FOLDER = '#{name}\'s bookmarks'
DEFAULT_SEARCH_FOLDER = '#PixivSearch_{keyword}_{search_type}_{match}_{sort}_{search_range}_{popularity}_{limit}'
DEFAULT_RANK_FOLDER = '#PixivRanking_{date}_{rank_type}_{content}_{limit}'

"""
String to clear previous stdout line
"""
CLEAR_LINE = '\r' + ' ' * 150 + '\r'

"""
Indicate a failure when there's too much exceptions occurred during requesting in the same loop
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
MAX_PAGES_PER_ARTWORK = None

"""
file for saving cookies
"""
COOKIES_FILE = 'cookies.data'

"""
default whether to log requests to stdout
"""
LOG_REQUEST = False

"""
folder used when testing, do not run test if you are using folder of this name
or change this name before running test
"""
TEST_FOLDER = '#test_folder'

"""
user name and password used to login
"""
username = 'restorecyclebin@gmail.com'
password = '123456'
