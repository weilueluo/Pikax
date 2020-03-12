import os


class LanguageHandler:
    LANGS = ['English', 'Chinese']

    def __init__(self, default):
        if default not in self.LANGS:
            raise ValueError(f'Language given not supported: {default} is not in {self.LANGS}')
        self.lang = default

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)
        if isinstance(attr, dict):
            return attr[self.lang]
        else:
            return attr

    def __setattr__(self, key, value):
        if key == 'lang' and value not in self.LANGS:
            raise ValueError(f'Given language is not supported: {value} is not in {self.LANGS}')
        return super().__setattr__(key, value)

    # Android Client
    ACCESS_TOKEN_UPDATE_INTERNAL_ERROR = {
        'English': 'Internal Error: Update access token failed',
        'Chinese': '内部错误：Access token 更新失败'
    }
    INVALID_SEARCH_TYPE_ERROR = {
        'English': 'Search Type: {search_type} is not type of {search_types}',
        'Chinese': '搜索类型：{search_type}，不是 {search_types} 的一员'
    }
    INVALID_BOOKMARK_TYPE_ERROR = {
        'English': 'Bookmark type: {bookmark_type} is not type of {bookmark_types}',
        'Chinese': '书签类型：{bookmark_type}，不是 {bookmark_types} 的一员'
    }
    INVALID_MATCH_TYPE_ERROR = {
        'English': 'Match type: {match_type} is not type of {match_types}',
        'Chinese': '吻合类型：{match_type}，不是 {match_types} 的一员'
    }
    INVALID_SORT_TYPE_ERROR = {
        'English': 'Sort type: {sort_type} is not type of {sort_types}',
        'Chinese': '排序类型：{sort_type}，不是 {sort_types} 的一员'
    }
    INVALID_SEARCH_RANGE_ERROR = {
        'English': 'Search range: {search_range} is not type of {search_ranges}',
        'Chinese': '排序类型：{search_range}，不是 {search_ranges} 的一员'
    }
    INVALID_RESTRICT_TYPE_ERROR = {
        'English': 'Restrict type: {restrict_type} is not type of {restrict_types}',
        'Chinese': '限制类型：{restrict_type}，不是 {restrict_types} 的一员'
    }
    INVALID_CREATION_TYPE_ERROR = {
        'English': 'Creation type: {creation_type} is not type of {creation_types}',
        'Chinese': '作品类型：{creation_type} 不是 {creation_types} 的一员'
    }
    USER_DETAILS_CONFIG_ERROR = {
        'English': 'Failed to configure user id: {id} details: {e}',
        'Chinese': '配置用户 id: {id} 的信息失败: {e}'
    }
    GET_FOLLOWING_FAILED = {
        'English': 'Failed to get followings from user id: {id}',
        'Chinese': '获取用户：{id} 的关注失败'
    }

    # Artwork
    ARTWORK_CONFIGURE_ERROR = {
        'English': 'Failed to configure Artwork with id: {id}',
        'Chinese': '配置画作失败，画作id： {id}'
    }

    # Models
    DOWNLOAD_STATUS_OK = {
        'English': '[OK]',
        'Chinese': '[OK]'
    }
    DOWNLOAD_STATUS_SKIP = {
        'English': '[skipped]',
        'Chinese': '[跳过]'
    }
    DOWNLOAD_STATUS_FAIL = {
        'English': '[failed]',
        'Chinese': '[失败]'
    }
    INVALID_PROCESS_TYPE_ERROR = {
        'English': 'Process type: {process_type} is not type of {process_types}',
        'Chinese': '处理类型：{process_type}，不是 {process_types} 的一员'
    }
    ARTWORK_ID_PROCESSING = {
        'English': 'Processing artwork ids',
        'Chinese': '正在处理作品id'
    }
    ARTWORK_ID_PROCESS_RESULT = {
        'English': 'expected: {total} | success: {successes} | failed: {fails}',
        'Chinese': '期望: {total} | 成功: {successes} | 失败: {fails}'
    }

    # downloader
    ARTWORK_DETAIL_MESSAGE = {
        'English': '[{title}] p{page_num} by [{author}]',
        'Chinese': '[{title}] p{page_num} 来自 [{author}]'
    }

    # items
    ATTEMPT_ANDROID_LOGIN = {
        'English': 'Attempting Android login ... ',
        'Chinese': '正在尝试安卓登录 。。。 '
    }
    ATTEMPT_WEB_LOGIN = {
        'English': 'Attempting Web login ... ',
        'Chinese': '正在尝试网页登录 。。。 '
    }
    ANDROID_LOGIN_FAILED = {
        'English': 'Android login failed' + os.linesep + 'Reason: {e}',
        'Chinese': '安卓登录失败' + os.linesep + '原因：{e}'
    }
    WEB_LOGIN_FAILED = {
        'English': 'Web login failed' + os.linesep + 'Reason: {e}',
        'Chinese': '网页登录失败' + os.linesep + '原因：{e}'
    }
    LOGIN_STATUS = {
        'English': 'Login Status: {login_status}, API Client: {client}',
        'Chinese': '登录状态: {login_status}, 接口: {client}'
    }

    # models
    ARTWORK_DOWNLOAD_INFO = {
        'English': 'Downloading Artworks | {total_pages} pages from {total_artworks} artworks',
        'Chinese': '正在下载作品 | 从 {total_artworks} 中提取 {total_pages} 页'
    }
    DOWNLOADED_PAGES_INFO = {
        'English': 'There are {successes} downloaded pages',
        'Chinese': '成功下载 {successes} 页'
    }
    SKIPPED_PAGES_INFO = {
        'English': 'There are {skips} skipped pages',
        'Chinese': '跳过 {skips} 页'
    }
    FAILED_PAGES_INFO = {
        'English': 'There are {fails} failed pages',
        'Chinese': '失败 {fails} 页'
    }
    FILTER_INFO = {
        'English': 'Filtering {name} {operator_symbol} {value}',
        'Chinese': '过滤 {name} {operator_symbol} {value}'
    }
    DONE_INFO = {
        'English': '[ done ] {old} => {new}',
        'Chinese': '[ 完成 ] {old} => {new}'
    }
    DONE_MSG = {
        'English': ' [ done ] => {msg}',
        'Chinese': ' [ 完成 ] => {msg}'
    }
    DONE = {
        'English': ' [ done ]',
        'Chinese': ' [ 完成 ]'
    }
    DONE_TIME_TAKEN = {
        'English': ' [ done ] => {time_taken:.2f}s',
        'Chinese': ' [ 完成 ] => {time_taken:.2f} 秒'
    }

    # params
    INVALID_CONTENT_TYPE_ERROR = {
        'English': 'Content Type: {content_type} is not type of {content_types}',
        'Chinese': '内容类型：{content_type}，不是 {content_types} 的一员'
    }

    # result
    INCOMPATIBLE_TYPE_OPERATION = {
        'English': 'PikaxResults are in different type: {type1} and {type2}',
        'Chinese': '试图对不同类型的PikaxResults进行操作: {type1} 和 {type2}'
    }
    ADD_FOLDER_CONNECT = {
        'English': '_added_to',
        'Chinese': '_加_'
    }
    SUB_FOLDER_CONNECT = {
        'English': '_subtracted_by',
        'Chinese': '_减_'
    }

    # user
    USER_BOOKMARKS_RETRIEVE_FAILED = {
        'English': 'Failed to retrieve bookmark ids from user with id: {id}',
        'Chinese': '从用户id为：{id} 获取书签失败'
    }
    USER_BOOKMARKS_PROCESS_FAILED = {
        'English': 'Failed to process bookmark ids from user with id: {id}',
        'Chinese': '处理用户id为：{id} 的书签时失败'
    }

    # util
    REQUEST_INFO = {
        'English': '{req_type}: [{url}] params: [{params}]',
        'Chinese': '{req_type}: [{url}] 参数: [{params}]',
    }
    REQUEST_FALSEY = {
        'English': 'Requests returned Falsey, retries: {retries}',
        'Chinese': '请求返回错误，重试：{retries}'
    }
    REQUEST_INVALID_STATUS_CODE = {
        'English': 'HTTP Status code error >= 400: {status_code}, retries: {retries}',
        'Chinese': 'HTTP 状态码 >= 400: {status_code}, 重试: {retries}'
    }
    REQUEST_TIME_OUT = {
        'English': 'Request timeout: retries: {retries}',
        'Chinese': '请求超时：重试：{retries}'
    }
    REQUEST_EXCEPTION = {
        'English': 'Request exception encountered, retries: {retries}',
        'Chinese': '请求时出错，重试：{retries}'
    }
    REQUEST_REASON = {
        'English': 'Reason: {e}',
        'Chinese': '原因：{e}'
    }
    REQUEST_MSG = {
        'English': 'Message: {msg}',
        'Chinese': '信息：{msg}'
    }
    REQUEST_EXCEPTION_MSG = {
        'English': '{req_type} Failed: [{url}] params: [{params}]',
        'Chinese': '{req_type} 失败: [{url}] 参数: [{params}]',
    }

    # util
    TRIM_MSG = {
        'English': 'Trimmed {old_len} items => {new_len} items',
        'Chinese': '缩减 {old_len} 件 => {new_len} 件'
    }
    TRIM_NOT_NEEDED = {
        'English': 'Number of items are less than limit: {len} < {limit}',
        'Chinese': '件数少于限制: {len} < {limit}'
    }
    PROGRESS_WITH_TIME_LEFT = {
        'English': '{curr} / {total} => {curr_percent}% | Time Left est. {time_left:.2f}s',
        'Chinese': '{curr} / {total} => {curr_percent}% | 剩余时间估算： {time_left:.2f} 秒'
    }
    PROGRESS_TEXT = {
        'English': '{curr} / {total} => {curr_percent}%',
        'Chinese': '{curr} / {total} => {curr_percent}%'
    }


texts = LanguageHandler(LanguageHandler.LANGS[0])
