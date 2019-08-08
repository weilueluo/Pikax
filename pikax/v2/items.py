import enum
import os
import pickle
import re

from ..exceptions import LoginError, ReqException
from ..api.androidclient import AndroidClient
from ..api.webclient import WebClient
from ..api.defaultclient import DefaultAPIClient
from .. import util, settings


class LoginHandler:
    class LoginStatus(enum.Enum):
        PC = enum.auto()
        ANDROID = enum.auto()
        LOG_OUT = enum.auto()

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        try:
            util.log('Attempting Web Login ...')
            client = WebClient(self.username, self.password)
            util.log(f'Login successfully: {self.LoginStatus.PC}, client: {client}')
            return self.LoginStatus.PC, client
        except LoginError as e:
            util.log(f'Web Login failed: {e}')

        try:
            util.log('Attempting Android Login ...')
            client = AndroidClient(self.username, self.password)
            util.log(f'Login successfully: {self.LoginStatus.PC}, client: {client}')
            return self.LoginStatus.ANDROID, client
        except LoginError as e:
            util.log(f'Android Login failed: {e}')

        return self.LoginStatus.LOG_OUT, DefaultAPIClient()


def main():
    from .. import settings
    loginer = LoginHandler(settings.username, settings.password)
    status, client = loginer.login()
    print(status, client)


if __name__ == '__main__':
    main()
