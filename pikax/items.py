import enum
import os

from . import util
from .api.androidclient import AndroidAPIClient
from .api.defaultclient import DefaultAPIClient
from .api.webclient import WebAPIClient
from .exceptions import LoginError
from .texts import texts

__all__ = ['LoginHandler']


class LoginHandler:
    class LoginStatus(enum.Enum):
        PC = enum.auto()
        ANDROID = enum.auto()
        LOG_OUT = enum.auto()

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def web_login(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

        try:
            util.log(texts.ATTEMPT_WEB_LOGIN)
            return self.LoginStatus.PC, WebAPIClient(self.username, self.password)
        except LoginError as e:
            util.log(texts.WEB_LOGIN_FAILED.format(e=e))
            return self.LoginStatus.LOG_OUT, DefaultAPIClient()

    def android_login(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

        try:
            util.log(texts.ATTEMPT_ANDROID_LOGIN)
            return self.LoginStatus.ANDROID, AndroidAPIClient(self.username, self.password)
        except LoginError as e:
            util.log(texts.ANDROID_LOGIN_FAILED.format(e=e))
            return self.LoginStatus.LOG_OUT, DefaultAPIClient()

    def login(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

        try:
            util.log(texts.ATTEMPT_ANDROID_LOGIN)

            client = AndroidAPIClient(self.username, self.password)
            login_status = self.LoginStatus.ANDROID

        except LoginError as e:
            util.log(texts.ANDROID_LOGIN_FAILED.format(e=e))

            client = DefaultAPIClient()
            login_status = self.LoginStatus.LOG_OUT

        util.log(texts.LOGIN_STATUS.format(login_status=login_status, client=client), start=os.linesep, inform=True)
        return login_status, client
