import sys

from lib.pikax import params
from lib.pikax.exceptions import PikaxException, ArtworkError
from lib.pikax.items import LoginHandler
from lib.pikax.pikax import Pikax
from lib.pikax.result import DefaultPikaxResult


class PikaxHandler:
    def __init__(self):
        self.pikax = Pikax()
        self.user = None
        self.logged = False

    def login(self, username, password):
        status, client = LoginHandler().android_login(username, password)
        if status is LoginHandler.LoginStatus.ANDROID:
            self.pikax.android_client = client
            self.logged = True
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

    def download_by_illust_ids(self, illust_ids):
        try:
            artworks, fails = self.pikax.get_id_processor().process(ids=illust_ids, process_type=params.ProcessType.ILLUST)
            result = DefaultPikaxResult(artworks, download_type=params.DownloadType.ILLUST)
            self.pikax.download(result)
        except ArtworkError as e:
            sys.stdout.write(str(e) + '\n' + 'Likely due to Id does not exists')

    def download_by_artist_id(self, artist_id, limit, content, folder):
        try:
            artist = self.pikax.visits(user_id=artist_id)

            if content is params.ContentType.ILLUST:
                result = artist.illusts(limit=limit)
            elif content is params.ContentType.MANGA:
                result = artist.mangas(limit=limit)
            else:
                result = artist.bookmarks(limit=limit)

            self.pikax.download(result, folder=folder)
        except PikaxException as e:
            sys.stdout.write(str(e))
