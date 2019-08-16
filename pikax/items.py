import enum
import os

from .exceptions import LoginError
from .api.androidclient import AndroidAPIClient
from .api.webclient import WebAPIClient
from .api.defaultclient import DefaultAPIClient
from . import util


class LoginHandler:
    class LoginStatus(enum.Enum):
        PC = enum.auto()
        ANDROID = enum.auto()
        LOG_OUT = enum.auto()

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def web_login(self, username=None, password=None):
        if username and password:
            self.username = username
            self.password = password

        try:
            util.log('Attempting Web Login ...')
            return self.LoginStatus.PC, WebAPIClient(self.username, self.password)
        except LoginError as e:
            util.log(f'web login failed: {e}')
            return self.LoginStatus.LOG_OUT, DefaultAPIClient()

    def android_login(self, username=None, password=None):
        if username and password:
            self.username = username
            self.password = password

        try:
            util.log('Attempting Android Login ...')
            return self.LoginStatus.ANDROID, AndroidAPIClient(self.username, self.password)
        except LoginError as e:
            util.log(f'android login failed: {e}')
            return self.LoginStatus.LOG_OUT, DefaultAPIClient()

    def login(self, username=None, password=None):
        if username and password:
            self.username = username
            self.password = password

        try:
            util.log('Attempting Web Login ...')

            client = WebAPIClient(self.username, self.password)
            login_status = self.LoginStatus.PC

        except LoginError as e:
            util.log(f'Web Login failed: {e}')
            try:
                util.log('Attempting Android Login ...')

                client = AndroidAPIClient(self.username, self.password)
                login_status = self.LoginStatus.ANDROID

            except LoginError as e:
                util.log(f'Android Login failed: {e}')

                client = DefaultAPIClient()
                login_status = self.LoginStatus.LOG_OUT

        util.log(f'Login Status: {login_status}, API Client: {client}', start=os.linesep, inform=True)
        return login_status, client


def main():
    from . import settings
    loginer = LoginHandler(settings.username, settings.password)
    status, client = loginer.web_login()
    assert status is LoginHandler.LoginStatus.PC
    status, client = loginer.android_login()
    assert status is LoginHandler.LoginStatus.ANDROID

    print('Successfully tested login handler')

if __name__ == '__main__':
    main()
