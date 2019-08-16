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

    def rank(self):
        ...

    def search(self, keyword, limit, sort, match, popularity, folder):

        result = self.pikax.search(keyword=keyword, limit=limit, sort=sort, match=match, popularity=popularity)
        for curr, total, info in self.pikax.download(result, folder):
            print(curr, total, info)

