import os

import pikax
import settings

#
# do not remove curly brackets or change word inside
#

# Global Settings
LANGS = ['English', '中文']
LANG = LANGS[0]

GUI_LANG_TO_PIKAX_LANG = {
    'English': 'English',
    '中文': 'Chinese'
}


def set_next_lang():
    global LANGS
    next_index = (LANGS.index(LANG) + 1) % len(LANGS)
    set_lang(LANGS[next_index])


def set_lang(lang):
    global LANG
    global LANGS
    if lang not in LANGS:
        raise KeyError(f'Given language: {lang} is not in supported languages: {LANGS}')
    LANG = lang
    pikax.texts.lang = GUI_LANG_TO_PIKAX_LANG[LANG]


def get(key):
    try:
        return globals()[key][LANG]
    except AttributeError as e:
        return f'Internal Error: {e}'


def values_translate(key, value, src_lang, dest_lang):
    globs = globals()
    src_dropdown = globs[key][src_lang]
    index = src_dropdown.index(value)
    dest_dropdown = globs[key][dest_lang]
    return dest_dropdown[index]


#
# General
#

TITLE = {
    'English': 'Pikax',
    '中文': 'Pikax'
}

TITLE_TEXT = {
    'English': get('TITLE') + ' ' + settings.VERSION,
    '中文': get('TITLE') + ' ' + settings.VERSION
}

FRAME_TITLE = {
    'English': 'Pikax - Pixiv Downloader',
    '中文': 'Pikax - Pixiv 下载器'  # frame never get refresh so this is actually never used
}

BULLET = {
    'English': '\u2022',
    '中文': '\u2022'
}

CROSS = {
    'English': '\u2718',
    '中文': '\u2718'
}

TICK = {
    'English': '\u2714',
    '中文': '\u2714'
}

FILE_CORRUPTED = {
    'English': '{file} is corrupted, removed\nmessage: {msg}',
    '中文': '{file} 损坏，已删除\n消息: {msg}'
}

DONE = {
    'English': 'Done',
    '中文': '完成'
}

LIMIT_CHOICES = {
    'English': ['pages limit', 'artworks limit'],
    '中文': ['页数限额', '作品限额']
}

#
# Models
#


MODELS_ISSUE_TEXT = {
    'English': 'Report',
    '中文': '反馈'
}

MODELS_ARTIST_REFERENCE_TEXT = {
    'English': '*background by {artist_name}',
    '中文': '*背景画师为 {artist_name}'
}

MODELS_INVALID_ROW_ERROR = {
    'English': 'Invalid row: {row}, expected: 0 <= row <= {grid_height}',
    '中文': '行数不正确：{row}, 预期：0 <= 行 <= {grid_height}'
}

MODELS_INVALID_COLUMN_ERROR = {
    'English': 'Invalid column: {column}, expected: 0 <= column <= {grid_width}',
    '中文': '列数不正确：{column}, 预期：0 <= 列 <= {grid_width}'
}

MODELS_INVALID_ROWSPAN_ERROR = {
    'English': 'Invalid rowspan: {rowspan}, expected: 0 <= {row} + rowspan <= {grid_height}',
    '中文': '行跨度不正确：{rowspan}, 预期：0 <= {row} + 行跨度 <= {grid_height}'
}

MODELS_INVALID_COLUMNSPAN_ERROR = {
    'English': 'Invalid columnspan: {columnspan}, expected: 0 <= {column} + columnspan <= {grid_width}',
    '中文': '列跨度不正确：{columnspan}, 预期：0 <= {column} + 列跨度 <= {grid_width}'
}

MODELS_SWITCHBUTTON_INVALID_SET_VALUE = {
    'English': 'Internal Error: Switch Button set value: {value} is not in {values}',
    '中文': '内部错误：转换按钮设置数值：{value} 不在范围：{values} 中'
}

MODELS_DOWNLOAD_FOLDER = {
    'English': 'Images downloaded to folder: {folder}',
    '中文': '作品已下载至文件夹：{folder}'
}

#
# Login screen
#


LOGIN_USERNAME = {
    'English': 'pixiv email/username',
    '中文': 'Pixiv 邮箱/用户名'
}

LOGIN_PASSWORD = {
    'English': 'pixiv password',
    '中文': 'Pixiv 密码'
}

LOGIN_LOGIN_BUTTON = {
    'English': 'Login',
    '中文': '登录'
}

LOGIN_GUEST_BUTTON = {
    'English': 'Guest',
    '中文': '游客'
}

LOGIN_REGISTER_BUTTON = {
    'English': 'Register',
    '中文': '注册'
}

LOGIN_REMEMBER_TEXT = {
    'English': 'Remember Me',
    '中文': '记住我'
}

ANDROID_LOGGING_TEXT = {
    'English': 'Attempting Login ...',
    '中文': '正在尝试登录 。。。'
}

ANDROID_LOGIN_FAILED = {
    'English': 'android login failed: {e}',
    '中文': '安卓登录失败：{e}'
}

#
# Account
#
ACCOUNT_USERNAME_CORRUPTED = {
    'English': 'username corrupted',
    '中文': '用户名损坏'
}

ACCOUNT_PASSWORD_CORRUPTED = {
    'English': 'password corrupted',
    '中文': '密码损坏'
}

#
# Illustration screen
#


ILLUSTRATION_ID_OR_URL = {
    'English': 'Illustration ID or URL (s)',
    '中文': '画作 ID 或者 网址'
}

ILLUSTRATION_DOWNLOAD = {
    'English': 'Download',
    '中文': '下载'
}

ILLUSTRATION_BACK = {
    'English': 'Back',
    '中文': '返回'
}

ILLUSTRATION_NO_ID_FOUND = {
    'English': 'No valid ID found in input\nshould be exactly 8 digits number',
    '中文': '未在输入中找到可用ID\n应为8位数'
}

#
# Artist
#


ARTIST_ID_OR_URL = {
    'English': 'Artist ID or URL',
    '中文': '画师 ID 或者 网址'
}

ARTIST_DOWNLOAD = {
    'English': 'Download',
    '中文': '下载'
}

ARTIST_BACK = {
    'English': 'Back',
    '中文': '返回'
}

ARTIST_CONTENT_SWITCH_VALUES = {
    'English': ['Illustrations', 'Mangas', 'Bookmarks'],
    '中文': ['插画', '漫画', '收藏']
}

ARTIST_CONTENT_TEXT = {
    'English': 'Type',
    '中文': '类型'
}

ARTIST_LIMIT_TEXT = {
    'English': 'Limit',
    '中文': '限额'
}

ARTIST_DOWNLOAD_FOLDER = {
    'English': 'Download Folder',
    '中文': '下载文件夹'
}

ARTIST_NO_ID_FOUND = {
    'English': 'No ID found in input\nShould contains a sequence of digits',
    '中文': '未在输入中找到 ID\n应含有一串数字'
}

ARTIST_AMBIGUOUS_ID_FOUND = {
    'English': 'Multiple sequence of digits found\nPlease provide 1 artist ID only',
    '中文': '找到多串数字\n请只提供一个画师的ID'
}

ARTIST_LIKES_TEXT = {
    'English': 'Likes Above',
    '中文': '赞大于'
}

#
# Menu Screen
#


MENU_RANK = {
    'English': 'Rank',
    '中文': '排行榜'
}

MENU_ID = {
    'English': 'Illustration',
    '中文': '插画'
}

MENU_SEARCH = {
    'English': 'Search',
    '中文': '搜索'
}

MENU_BACK = {
    'English': 'Back',
    '中文': '返回'
}

MENU_ARTIST = {
    'English': 'Artist',
    '中文': '画师'
}

#
# Rank Screen
#


RANK_DATE = {
    'English': 'date',
    '中文': '日期'
}

RANK_LIMIT = {
    'English': 'limit',
    '中文': '限额'
}

RANK_TYPE = {
    'English': 'rank_type',
    '中文': '类型'
}

RANK_CONTENT = {
    'English': 'content',
    '中文': '内容'
}

RANK_DOWNLOAD_FOLDER = {
    'English': 'download folder',
    '中文': '下载文件夹'
}

RANK_TYPES = {
    'English': ['daily', 'weekly', 'monthly', 'rookie'],
    '中文': ['每日', '每周', '每月', '新人']
}

RANK_CONTENT_TYPES = {
    'English': ['illustration', 'manga'],
    '中文': ['插画', '漫画']
}

RANK_BACK = {
    'English': 'Back',
    '中文': '返回'
}

RANK_DOWNLOAD = {
    'English': 'Download',
    '中文': '下载'
}

RANK_LIMIT_ERROR = {
    'English': 'Limit must be an integer or empty',
    '中文': '限额需为正数或留空'
}

RANK_DATE_ERROR = {
    'English': 'Date must be a sequence of 8 digits',
    '中文': '日期必须为连续的8位数字'
}

RANK_INVALID_FOLDER_ERROR = {
    'English': 'Folder name contains invalid character(s)',
    '中文': '文件夹名称含有不被允许的字符'
}

RANK_ERROR_MESSAGE = {
    'English': 'Please check your inputs\nError message: {error_message}',
    '中文': '请检查你的输入\n异常消息：{error_message}'
}

#
# Search Screen
#

SEARCH_KEYWORD = {
    'English': 'Keyword',
    '中文': '关键字'
}

SEARCH_LIMIT = {
    'English': 'Limit',
    '中文': '限额'
}

SEARCH_MATCH = {
    'English': 'Tag Match',
    '中文': '标签吻合'
}

SEARCH_SORT = {
    'English': 'Sort',
    '中文': '排序'
}

SEARCH_POPULARITY = {
    'English': 'Popularity',
    '中文': '名气'
}

SEARCH_DOWNLOAD_FOLDER = {
    'English': 'Download Folder',
    '中文': '下载文件夹'
}

SEARCH_MATCH_CHOICES = {
    'English': ['Exact', 'Partial', 'Any'],
    '中文': ['准确', '局部', '任何']
}

SEARCH_SORT_CHOICES = {
    'English': ['Date Ascending', 'Date Descending'],
    '中文': ['日期小到大', '日期大到小']
}

SEARCH_POPULARITY_CHOICES = {
    'English': ['Any', '100', '500', '1000', '5000', '10000', '20000'],
    '中文': ['任何', '100', '500', '1000', '5000', '10000', '20000']
}

SEARCH_DOWNLOAD = {
    'English': 'Download',
    '中文': '下载'
}

SEARCH_BACK = {
    'English': 'Back',
    '中文': '返回'
}

SEARCH_EMPTY_KEYWORD_ERROR = {
    'English': 'Keyword cannot be empty',
    '中文': '关键字不能为空'
}

SEARCH_INVALID_FOLDER_ERROR = {
    'English': 'Folder name contains invalid characters',
    '中文': '文件夹名称含有不被允许的字符'
}

SEARCH_LIMIT_ERROR = {
    'English': 'Limit must be a integer or empty',
    '中文': '限额需为正数或留空'
}

SEARCH_ERROR_MESSAGE = {
    'English': 'Please check your inputs\nError Message: {error_message}',
    '中文': '请检查你的输入\n异常消息：{error_message}'
}

DOWNLOADER_CANCEL = {
    'English': 'Cancel',
    '中文': '取消'
}

DOWNLOADER_DONE = {
    'English': 'Done',
    '中文': '完成'
}

#
# Downloader
#


DOWNLOAD_INITIALIZING = {
    'English': 'Initializing Download of Artworks | {total_pages} pages from {total_artworks} artworks',
    '中文': '正在初始化下载作品 | {total_artworks} 画作中提取 {total_pages} 页'
}

##
# Pikax Handler
##

#
# Models
#

DOWNLOAD_FINISHED_SUCCESS_PAGES = {
    'English': 'There are {successes} downloaded pages\n',
    '中文': '下载总共 {successes} 页\n'
}

DOWNLOAD_FINISHED_SKIPPED_PAGES = {
    'English': 'There are {skips} skipped pages\n',
    '中文': '跳过总共 {skips} 页\n'
}

DOWNLOAD_FINISHED_SKIPPED_INFO = {
    'English': '[{counter}] {skip_info}\n',
    '中文': '[{counter}] {skip_info}\n'
}

DOWNLOAD_FINISHED_FAILED_PAGES = {
    'English': 'There are {fails} failed pages\n',
    '中文': '失败总共 {fails} 页\n'
}

DOWNLOAD_FINISHED_FAILED_INFO = {
    'English': '[{counter}] {fail_info}\n',
    '中文': '[{counter}] {fail_info}\n'
}

DOWNLOAD_FINISHED_PATH_NOTICE = {
    'English': '\nDownloaded to\n{download_path}',
    '中文': '已下载到\n{download_path}'
}

DOWNLOAD_STATUS_OK = {
    'English': '[OK]',
    '中文': '【完成】'
}

DOWNLOAD_STATUS_SKIPPED = {
    'English': '[skipped]',
    '中文': '【跳过】'
}

DOWNLOAD_STATUS_FAILED = {
    'English': '<failed>',
    '中文': '《失败》'
}

PROCESS_ID_TITLE = {
    'English': 'ID Processing',
    '中文': 'ID 处理中'
}

PROCESS_ID_INITIALIZING = {
    'English': 'Processing artwork ids',
    '中文': '正在处理画作 IDs'
}

PROCESS_FINISHED_MESSAGE = {
    'English': 'Expected: {total} | Success: {successes} | Failed: {fails}\n\nID Processing Finished',
    '中文': '期望: {total} | 成功: {successes} | 失败: {fails}\n\nID 处理结束'
}

PROCESS_TYPE_ERROR = {
    'English': 'process rank_type: {process_type} is not rank_type of {process_class}',
    '中文': '排行榜种类: {process_type} 并不是 {process_class} 的一员'
}

BY = {
    'English': 'by',
    '中文': '来自'
}

#
# PikaxHandler
#


PIKAX_FAILED_LOGIN = {
    'English': 'Failed Login',
    '中文': '登录失败'
}

PIKAX_RANK_FAILED = {
    'English': 'Rank & download failed, message:{error}',
    '中文': '排行榜下载失败, 消息：{error}'
}

PIKAX_SEARCH_FAILED = {
    'English': 'Search & download failed, message:{error}',
    '中文': '搜索并下载失败, 消息：{error}'
}

PIKAX_ILLUST_ID_FAILED = {
    'English': '{error} Likely due to Illustration of this ID does not exists',
    '中文': '{error} 通常是因为这个ID的画作不存在'
}

#
# PikaxAPI
#


API_ID_COLLECTED = {
    'English': 'ID Collected: {ids_len} {limit_str}',
    '中文': '已收集的ID：{ids_len} {limit_str}'
}

#
# Download Screen
#


DOWNLOAD_INITIALIZE_FAILED = {
    'English': 'Initialization Failed',
    '中文': '初始化失败'
}

TIME_LEFT_EST = {
    'English': 'Time Left est.',
    '中文': '剩余时间估算'
}

SECOND = {
    'English': 's',
    '中文': '秒'
}

#
# Utilities
#

UTIL_TRIMMED = {
    'English': 'Trimmed',
    '中文': '裁'
}

UTIL_ITEMS = {
    'English': 'items',
    '中文': '物品'
}

UTIL_TRIM_NUM_ITEMS_LESS_THAN_LIMIT_ERROR = {
    'English': 'Number of items are less than limit:',
    '中文': '物品数量小于限额'
}
