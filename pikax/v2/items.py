import enum
import os

from ..exceptions import LoginError
from ..api.androidclient import AndroidAPIClient
from ..api.webclient import WebAPIClient
from ..api.defaultclient import DefaultAPIClient
from .. import util


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
    from .. import settings
    loginer = LoginHandler(settings.username, settings.password)
    status, client = loginer.login()
    print(status, client)


if __name__ == '__main__':
    main()
