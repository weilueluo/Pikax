import os
import sys

import pikax
import texts
from pikax import Pikax, ArtworkError, DefaultPikaxResult
from pikax import params
from pikax import settings
from pikax import util
from pikax.exceptions import PikaxException
from pikax.items import LoginHandler


class PikaxHandler:
    def __init__(self):
        self.pikax = Pikax()
        self.user = None
        self.logged = False

    def login(self, username, password):
        status, client = LoginHandler().android_login(username, password)
        if status is LoginHandler.LoginStatus.ANDROID:
            self.pikax.logged_client = client
            self.logged = True
        else:
            raise PikaxException(texts.get('PIKAX_FAILED_LOGIN'))

    def rank(self, rank_type, limit, date, content, folder, pages_limit):
        try:
            old_limit = settings.MAX_PAGES_PER_ARTWORK
            if pages_limit:
                settings.MAX_PAGES_PER_ARTWORK = 1
            result = self.pikax.rank(rank_type=rank_type, limit=limit, date=date, content=content)
            self.pikax.download(result, folder=folder)
            settings.MAX_PAGES_PER_ARTWORK = old_limit
        except PikaxException as e:
            import sys
            sys.stdout.write(texts.get('PIKAX_RANK_FAILED').format(error=e))

    def search(self, keyword, limit, sort, match, popularity, folder, pages_limit):
        try:
            old_limit = settings.MAX_PAGES_PER_ARTWORK
            if pages_limit:
                settings.MAX_PAGES_PER_ARTWORK = 1
            result = self.pikax.search(keyword=keyword, limit=limit, sort=sort, match=match, popularity=popularity)
            self.pikax.download(result, folder)
            settings.MAX_PAGES_PER_ARTWORK = old_limit
        except PikaxException as e:
            import sys
            sys.stdout.write(texts.get('PIKAX_SEARCH_FAILED').format(error=e))

    def download_by_illust_ids(self, illust_ids):
        try:
            artworks, fails = self.pikax.get_id_processor().process(ids=illust_ids,
                                                                    process_type=params.ProcessType.ILLUST)
            result = DefaultPikaxResult(artworks, download_type=params.DownloadType.ILLUST)
            self.pikax.download(result)
        except ArtworkError as e:
            sys.stdout.write(texts.get('PIKAX_ILLUST_ID_FAILED').format(error=e))

    def download_by_artist_id(self, artist_id, limit, content, folder, likes, pages_limit):
        try:
            old_limit = settings.MAX_PAGES_PER_ARTWORK
            if pages_limit:
                settings.MAX_PAGES_PER_ARTWORK = 1

            artist = self.pikax.visits(user_id=artist_id)

            content_to_method = {
                params.Content.ILLUST: artist.illusts,
                params.Content.MANGA: artist.mangas,
                params.BookmarkType.ILLUST_OR_MANGA: artist.bookmarks
            }
            if not likes:
                limit = None

            result = content_to_method[content](limit=limit)

            if likes:
                result = (result.likes > likes).renew_artworks(util.trim_to_limit(result.likes > likes, limit))

            self.pikax.download(result, folder=folder)

            settings.MAX_PAGES_PER_ARTWORK = old_limit

        except PikaxException as e:
            sys.stdout.write(str(e))


# log stuff
def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True, start='', inform=False, save=False, error=False,
        warn=False, normal=False):
    import sys
    string = str(start) + sep.join(str(obj) for obj in objects) + end
    sys.stdout.write(string)


pikax.util.log = log

pikax.texts.GUI_ARTWORK_DOWNLOAD_HEADING = {
    'English': 'Artwork Downloading' + os.linesep + os.linesep,
    'Chinese': '作品下载中' + os.linesep + os.linesep
}
pikax.texts.GUI_ID_PROCESSING_HEADING = {
    'English': 'Artwork ID Processing' + os.linesep,
    'Chinese': '作品ID处理中' + os.linesep
}


# request stuff
pikax.settings.TIMEOUT = 3
