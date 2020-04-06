import os

__all__ = ['LanguageHandler', 'texts', 'ZH', 'EN']


class LanguageHandler:
    LANGS = ['English', 'Chinese']
    ZH = 'Chinese'
    EN = 'English'

    def __init__(self, default):
        if default not in self.LANGS:
            raise ValueError(f'Language given not supported: {default} is not in {self.LANGS}')
        self.lang = default

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)
        if isinstance(attr, dict):
            try:
                return attr[self.lang]
            except TypeError:
                pass
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
    INVALID_DIMENSION_TYPE_ERROR = {
        'English': 'Dimension type: {dimension_type} is not type of {dimension_types}',
        'Chinese': '尺寸类型：{dimension_type}，不是 {dimension_types} 的一员'
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
        'Chinese': '配置画作失败，画作id：{id}'
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
    DOWNLOAD_FINISHED_INFO_FOLDER = {
        'English': f'Artworks downloaded to folder:{os.linesep}{{folder}}',
        'Chinese': f'作品已下载至文件夹：{os.linesep}{{folder}}'
    }

    # GUI uses:
    # a stub for gui to print heading when processing
    GUI_ID_PROCESSING_HEADING = {
        'English': '',
        'Chinese': ''
    }
    GUI_ARTWORK_DOWNLOAD_HEADING = {
        'English': '',
        'Chinese': ''
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
        'English': 'Downloading Artworks | extract {total_pages} pages from {total_artworks} artworks',
        'Chinese': '正在下载作品 | 从{total_artworks}作品中提取{total_pages}页'
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
        'Chinese': ' [ 完成 ] => {time_taken:.2f}秒'
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
    REQUEST_CONNECTION_ERROR = {
        'English': 'Request Connection Error: retries: {retries}',
        'Chinese': '请求链接出错：重试：{retries}'
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

    TRIM_MSG = {
        'English': 'Trimmed {old_len} => {new_len} items',
        'Chinese': '缩减 {old_len} => {new_len} 件'
    }
    TRIM_NOT_NEEDED = {
        'English': 'Number of items are less than limit: {len} < {limit}',
        'Chinese': '件数少于限制: {len} < {limit}'
    }
    PROGRESS_WITH_TIME_LEFT = {
        'English': '{curr} / {total} => {curr_percent:.2f}% | Time Left est. {time_left}',
        'Chinese': '{curr} / {total} => {curr_percent:.2f}% | 剩余时间估算：{time_left}'
    }
    TIME_LEFT_EST = {
        'English': 'Time Left est. {time_left}',
        'Chinese': '剩余时间估算：{time_left}'
    }
    PROGRESS_TEXT = {
        'English': '{curr} / {total} => {curr_percent:.2f}%',
        'Chinese': '{curr} / {total} => {curr_percent:.2f}%'
    }
    DOWNLOAD_PAGES_PROGRESS_TEXT = {
        'English': 'Pages: {curr} / {total} => {curr_percent:.2f}%',
        'Chinese': '页数：{curr} / {total} => {curr_percent:.2f}%'
    }
    DOWNLOAD_ARTWORK_PROGRESS_TEXT = {
        'English': 'Artworks: {curr} / {total} => {curr_percent:.2f}%',
        'Chinese': '作品：{curr} / {total} => {curr_percent:.2f}%'
    }
    TIME_FORMAT_HMS = {
        'English': '{h:.0f}h {m:.0f}m {s:.0f}s',
        'Chinese': '{h:.0f}时 {m:.0f}分 {s:.0f}秒'
    }
    TIME_FORMAT_MS = {
        'English': '{m:.0f}m {s:.0f}s',
        'Chinese': '{m:.0f}分 {s:.0f}秒'
    }
    TIME_FORMAT_S = {
        'English': '{s:.0f}s',
        'Chinese': '{s:.0f}秒'
    }

    # web client
    CHECK_LOGIN_FAILED = {
        'English': 'Login check Failed',
        'Chinese': '登录检测失败'
    }
    OVERWRITE_LOCAL_COOKIES = {
        'English': 'Overwriting local cookie file: {file}',
        'Chinese': '正在覆盖本地cookie'
    }
    SAVE_LOCAL_COOKIES = {
        'English': 'Saving cookie to local file: {file}',
        'Chinese': '正在将cookie保存至文件：{file}'
    }
    ATTEMPT_WEB_CLIENT_LOGIN = {
        'English': 'Sending request to attempt login',
        'Chinese': '正在发送请求尝试登录'
    }
    WEB_LOGIN_REQUEST_FAILED = {
        'English': 'Failed to send login request: {e}',
        'Chinese': '请求发送失败：{e}'
    }
    WEB_LOGIN_REQUEST_NOT_ACCEPTED = {
        'English': 'Login request is not accepted',
        'Chinese': '登录请求被拒绝'
    }
    WEB_LOGIN_POST_KEY_RETRIEVE_SUCCESS = {
        'English': 'Post key successfully retrieved: {post_key}',
        'Chinese': '成功取得Post密钥：{post_key}'
    }
    WEB_LOGIN_POST_KEY_RETRIEVE_Failed = {
        'English': 'Failed to retrieve post key: {e}',
        'Chinese': '没能成功取得Post密钥：{e}'
    }

    COOKIE_LOGIN_FAILED = {
        'English': 'Cookie login failed',
        'Chinese': '使用Cookie登录失败'
    }
    COOKIE_LOGIN_SUCCESS = {
        'English': 'Cookie login success',
        'Chinese': '使用Cookie登录成功'
    }
    COOKIE_FILE_NOT_FOUND = {
        'English': 'Local cookie file not found: {file}',
        'Chinese': '未能找到本地cookie文件：{file}'
    }
    COOKIE_FILE_FOUND = {
        'English': 'Local cookie file found: {file}',
        'Chinese': '本地cookie文件：{file}'
    }
    REMOVED_OUTDATED_COOKIE = {
        'English': 'Removed outdated cookies',
        'Chinese': '已移除过期的cookie'
    }
    REMOVED_CORRUPTED_COOKIE = {
        'English': 'Removed corrupted cookies: {e}',
        'Chinese': '已移除无法使用的cookie：{e}'
    }
    PROVIDE_NEW_COOKIE_PROMPT = {
        'English': 'Login with local cookies failed, would you like to provide a new cookies?' + os.linesep
                   + ' [y] Yesss!' + os.linesep
                   + ' [n] Noooo! (this option will attempt alternate login with username and password)',
        'Chinese': '本地cookie登录失败，是否提供新的cookie？' + os.linesep
                   + ' [y] 要的要的!' + os.linesep
                   + ' [n] 不要不要! (选择此选项会尝试其他登录方法)'
    }
    PROVIDE_NEW_COOKIE_PROMPT_ASK = {
        'English': ' [=] Please select an option:',
        'Chinese': ' [=] 请选择一个选项：'
    }
    INVALID_RESPOND_PROMPT = {
        'English': 'Please enter your answer as case-insensitive \'y\' or \'n\' or \'yes\' or \'no\'',
        'Chinese': '请输入其中一个选项： \'y\' or \'n\' or \'yes\' or \'no\' （不区分大小写）',
    }
    ENTER_NEW_COOKIE_PROMPT = {
        'English': ' [=] Please enter your cookies here, just php session id will work,' + os.linesep +
                   ' [=] e.g. PHPSESSIONID=1234567890:',
        'Chinese': ' [=] 请输入你的cookie, php session id即可,' + os.linesep +
                   ' [=] 示例 PHPSESSIONID=1234567890:'
    }
    NEW_COOKIE_LOGIN_FAILED = {
        'English': 'Login failed with new cookie entered, try again? [y/n]',
        'Chinese': '使用新cookie登录失败, 再次尝试? [y/n]'
    }
    COOKIE_ENTERED_INVALID = {
        'English': 'Cookie entered is invalid: {e}',
        'Chinese': '输入了无法使用的cookie：{e}'
    }
    TRY_AGAIN_PROMPT = {
        'English': 'Try again? [y/n]',
        'Chinese': '再次尝试? [y/n]'
    }
    BOOKMARK_INVALID_LIMIT = {
        'English': 'Bookmark limit is not int or None',
        'Chinese': '书签限额不是int也不是None'
    }
    USER_ILLUST_RETRIEVE_FAILED = {
        'English': 'Failed to retrieve illustration ids from user with id: {id}',
        'Chinese': '从用户id为：{id} 获取画作id失败'
    }
    USER_MANGA_RETRIEVE_FAILED = {
        'English': 'Failed to retrieve mangas ids from user with id: {id}',
        'Chinese': '从用户id为：{id} 获取漫画id失败'
    }
    WEB_CLIENT_CONFIGURE_FAILED = {
        'English': 'Web client configure failed: {e}',
        'Chinese': '网页接口配置失败：{e}'
    }

    # default client
    # fk this TODO: complete later
    FOUND_NUM_ID_INFO = {
        'English': 'Found: {num_ids} for <{keyword}> in {sec:.0f}s',
        'Chinese': '在{sec:.0f}秒为<{keyword}>找到{num_ids}ids'
    }


ZH = LanguageHandler.ZH
EN = LanguageHandler.EN

texts = LanguageHandler(EN)
