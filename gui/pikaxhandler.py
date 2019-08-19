
from lib.pikax.exceptions import PikaxException
from lib.pikax.items import LoginHandler
from lib.pikax.pikax import Pikax


class PikaxHandler:
    def __init__(self):
        self.pikax = Pikax()
        self.user = None

    def login(self, username, password):
        status, client = LoginHandler().android_login(username, password)
        if status is LoginHandler.LoginStatus.ANDROID:
            self.pikax.android_client = client
        else:
            raise PikaxException('Failed Login')

    def rank(self, rank_type, limit, date, content, folder):
        try:
            result = self.pikax.rank(rank_type=rank_type, limit=limit, date=date, content=content)
            self.pikax.download(result, folder=folder)
        except PikaxException as e:
            import sys
            sys.stdout.write(f'Rank & download failed, message:\n{e}')

    def search(self, keyword, limit, sort, match, popularity, folder):
        try:
            result = self.pikax.search(keyword=keyword, limit=limit, sort=sort, match=match, popularity=popularity)
            self.pikax.download(result, folder)
        except PikaxException as e:
            import sys
            sys.stdout.write(f'Search & download failed, message:\n{e}')
