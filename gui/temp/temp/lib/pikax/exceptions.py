"""
This module contains different exceptions for Pikax
"""


class PikaxException(Exception):
    """Base Exception for all exceptions in Pikax
    """
    pass


class ReqException(PikaxException):
    """
    This exception is raised when something when wrong with sending requests to servers

    **See Also**
    :func: util.req
    """
    pass


class PostKeyError(PikaxException):
    """When failed to retrieve post key during login

    This may be a direct cause of LoginError

    **See Also**
    :func: pages.LoginPage.login
    :class: LoginError
    """
    pass


class LoginError(PikaxException):
    """When attempt to login has failed

    **See Also**
    :func: pages.LoginPage.login
    """
    pass


class ArtworkError(PikaxException):
    """When failed to initialize a artwork object

    :func: items.Artwork.__init__
    """
    pass


class UserError(PikaxException):
    """When failed to initialize a User object

    **See Also**
    :func: items.User.__init__
    """
    pass


class SearchError(PikaxException):
    """When failed to initialize a search in SearchPage

    **See Also**
    :func: pages.SearchPage.search
    """
    pass


class RankError(PikaxException):
    pass


class BaseClientException(PikaxException):
    pass


class ClientException(BaseClientException):
    pass


class ProcessError(PikaxException):
    pass


class PikaxResultError(PikaxException):
    pass


class ParamsException(PikaxException):
    pass


class PikaxUserError(PikaxException):
    pass


class APIUserError(PikaxException):
    pass
