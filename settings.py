"""
default time out in seconds for requests
"""
TIMEOUT = 5


"""
default headers for sending requests
not all requests uses this headers
"""
DEFAULT_HEADERS = {
    'referer': 'https://www.pixiv.net/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}


"""
LOG_TYPE
'inform': print successive stage and error only
'std': allow print
'save': save error to LOG_FILE only
'inform save' or 'informsave': will do both inform and save only
'': log nothing

'inform' will overwrite 'std'
"""
LOG_TYPE = 'inform'


"""
file used to log error if save is included in LOG_TYPE
"""
LOG_FILE = 'log.txt'

"""
Folder format for downlaoding favorites
"""
FAV_DOWNLOAD_FOLDER = '#{username}\'s favs'

"""
user name and password used
"""
username = 'restorecyclebin@gmail.com'
password = '123456'
