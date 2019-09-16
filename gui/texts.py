import settings

#
# do not remove curly brackets or change word inside
#

# General
TITLE = 'Pikax'
TITLE_TEXT = TITLE + ' ' + settings.VERSION
FRAME_TITLE = 'Pikax - Pixiv Downloader'

BULLET = '\u2022'
CROSS = '\u2718'
TICK = '\u2714'

# Models
MODELS_ISSUE_TEXT = 'Report'
MODELS_ARTIST_REFERENCE_TEXT = '*background by {artist_name}'
MODELS_INVALID_ROW_ERROR = 'Invalid row: {row}, expected: 0 <= row <= {grid_height}'
MODELS_INVALID_COLUMN_ERROR = 'Invalid column: {column}, expected: 0 <= column <= {grid_width}'
MODELS_INVALID_ROWSPAN_ERROR = 'Invalid rowspan: {rowspan}, expected: 0 <= {row} + rowspan <= {grid_height}'
MODELS_INVALID_COLUMNSPAN_ERROR = 'Invalid columnspan: {columnspan}, ' \
                                  'expected: 0 <= {column} + columnspan <= {grid_width}'

# Login screen
LOGIN_USERNAME = 'username'
LOGIN_PASSWORD = 'password'
LOGIN_LOGIN_BUTTON = 'Login'
LOGIN_GUEST_BUTTON = 'Guest'
LOGIN_REGISTER_BUTTON = 'Register'
LOGIN_REMEMBER_TEXT = 'Remember Me'


# Illustration screen
ILLUSTRATION_ID_OR_URL = 'Illustration ID or URL (s)'
ILLUSTRATION_DOWNLOAD = 'Download'
ILLUSTRATION_BACK = 'Back'
ILLUSTRATION_NO_ID_FOUND = 'No valid ID found in input\nshould be exactly 8 digits number'


# Artist
ARTIST_ID_OR_URL = 'Artist ID or URL'
ARTIST_DOWNLOAD = 'Download'
ARTIST_BACK = 'Back'
ARTIST_CONTENT_SWITCH_VALUES = ['Illustrations', 'Mangas', 'Bookmarks']
ARTIST_CONTENT_TEXT = 'Content'
ARTIST_LIMIT_TEXT = 'Limit'
ARTIST_DOWNLOAD_FOLDER = 'Download Folder'
ARTIST_NO_ID_FOUND = 'No ID found in input\nShould contains a sequence of digits'
ARTIST_AMBIGUOUS_ID_FOUND = 'Multiple sequence of digits found\nPlease provide 1 artist ID only'

# menu screen
MENU_RANK = 'Rank'
MENU_ID = 'Illustration'
MENU_SEARCH = 'Search'
MENU_BACK = 'Back'
MENU_ARTIST = 'Artist'

# rank screen
RANK_DATE = 'date'
RANK_LIMIT = 'limit'
RANK_TYPE = 'type'
RANK_CONTENT = 'content'
RANK_DOWNLOAD_FOLDER = 'download folder'
RANK_TYPES = ['daily', 'weekly', 'monthly', 'rookie']
RANK_CONTENT_TYPES = ['illustration', 'manga']
RANK_BACK = 'Back'
RANK_DOWNLOAD = 'Download'
RANK_LIMIT_ERROR = 'Limit must be an integer or empty'
RANK_DATE_ERROR = 'Date must be a sequence of 8 digits'
RANK_INVALID_FOLDER_ERROR = 'Folder name contains invalid character(s)'
RANK_ERROR_MESSAGE = 'Please check your inputs\nError message: {error_message}'

# search screen
SEARCH_KEYWORD = 'Keyword'
SEARCH_LIMIT = 'Limit'
SEARCH_MATCH = 'Tag Match'
SEARCH_SORT = 'Sort'
SEARCH_POPULARITY = 'Popularity'
SEARCH_DOWNLOAD_FOLDER = 'Download Folder'
SEARCH_MATCH_CHOICES = ['Exact', 'Partial', 'Any']
SEARCH_SORT_CHOICES = ['Date Ascending', 'Date Descending']
SEARCH_POPULARITY_CHOICES = ['Any', '100', '500', '1000', '5000', '10000', '20000']
SEARCH_DOWNLOAD = 'Download'
SEARCH_BACK = 'Back'
SEARCH_EMPTY_KEYWORD_ERROR = 'Keyword cannot be empty'
SEARCH_INVALID_FOLDER_ERROR = 'Folder name contains invalid characters'
SEARCH_LIMIT_ERROR = 'Limit must be a integer or empty'
SEARCH_ERROR_MESSAGE = 'Please check your inputs\nError Message: {error_message}'

# downloader
DOWNLOADER_CANCEL = 'Cancel'

# Pikax Handler
# Models
DOWNLOAD_INITIALIZING = 'Initializing Download of Artworks | {total_pages} pages from {total_artworks} artworks'
DOWNLOAD_FINISHED_SUCCESS_PAGES = 'There are {successes} downloaded pages\n'
DOWNLOAD_FINISHED_SKIPPED_PAGES = 'There are {skips} skipped pages\n'
DOWNLOAD_FINISHED_SKIPPED_INFO = '[{counter}] {skip_info}\n'
DOWNLOAD_FINISHED_FAILED_PAGES = 'There are {fails} failed pages\n'
DOWNLOAD_FINISHED_FAILED_INFO = '[{counter}] {fail_info}\n'
DOWNLOAD_FINISHED_PATH_NOTICE = '\nDownloaded to\n{download_path}'
DOWNLOAD_STATUS_OK = '[OK]'
DOWNLOAD_STATUS_SKIPPED = '[skipped]'
DOWNLOAD_STATUS_FAILED = '<failed>'

PROCESS_ID_INITIALIZING = 'Processing artwork ids'
PROCESS_FINISHED_MESSAGE = 'Expected: {total} | Success: {successes} | Failed: {fails}\nID Processing Finished'
PROCESS_TYPE_ERROR = 'process type: {process_type} is not type of {process_class}'














