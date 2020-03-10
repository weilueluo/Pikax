class LanguageHandler:
    LANGS = ['English', 'Chinese']

    def __init__(self, default):
        if default not in self.LANGS:
            raise ValueError('Internal Error: default language given not supported')
        self.lang = default

    def __getattribute__(self, item):
        attr = self.__dict__[item]
        if isinstance(attr, dict):
            return attr[self.lang]
        else:
            return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key == 'lang' and value not in self.LANGS:
            raise ValueError('Internal Error: Given language is not supported')
        return super().__setattr__(key, value)

    # Android Client
    ACCESS_TOKEN_UPDATE_INTERNAL_ERROR = {
        'English': 'Internal Error: Failed update access token',
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


texts = LanguageHandler(LanguageHandler.LANGS[0])
