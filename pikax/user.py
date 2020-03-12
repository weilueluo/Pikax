from .models import PikaxUserInterface
from . import params, settings
from .processor import DefaultIDProcessor
from .exceptions import PikaxUserError
from .result import DefaultPikaxResult
from .models import PikaxResult
from .texts import texts
from .exceptions import APIUserError, ProcessError

__all__ = ['DefaultPikaxUser']


class DefaultPikaxUser(PikaxUserInterface):

    def __init__(self, client, user_id):
        self._client = client
        self._user = self._client.visits(user_id=user_id)
        self._id_processor = DefaultIDProcessor()
        self._illusts_folder = settings.DEFAULT_ILLUSTS_FOLDER
        self._mangas_folder = settings.DEFAULT_MANGAS_FOLDER
        self._bookmarks_folder = settings.DEFAULT_BOOKMARKS_FOLDER

    def illusts(self, limit: int = None) -> PikaxResult:
        ids = self._user.illusts(limit=limit)
        successes, fails = self._id_processor.process(ids, process_type=params.ProcessType.ILLUST)
        return DefaultPikaxResult(artworks=successes, download_type=params.DownloadType.ILLUST,
                                  folder=self._illusts_folder.format(name=self.name))

    def mangas(self, limit: int = None) -> PikaxResult:
        ids = self._user.mangas(limit=limit)
        successes, fails = self._id_processor.process(ids, process_type=params.ProcessType.MANGA)
        return DefaultPikaxResult(artworks=successes, download_type=params.DownloadType.MANGA,
                                  folder=self._mangas_folder.format(name=self.name))

    def bookmarks(self, limit: int = None,
                  bookmark_type: params.BookmarkType = params.BookmarkType.ILLUST_OR_MANGA) -> PikaxResult:
        try:
            ids = self._user.bookmarks(limit=limit, bookmark_type=bookmark_type)
        except APIUserError as e:
            raise PikaxUserError(texts.USER_BOOKMARKS_RETRIEVE_FAILED.format(id=self._user.id)) from e

        try:
            successes, fails = self._id_processor.process(ids, process_type=params.BookmarkType.map_bookmark_to_process(
                bookmark_type))
        except ProcessError as e:
            raise PikaxUserError(texts.USER_BOOKMARKS_PROCESS_FAILED.format(id=self._user.id)) from e

        return DefaultPikaxResult(artworks=successes,
                                  download_type=params.BookmarkType.map_bookmark_to_download(bookmark_type),
                                  folder=self._bookmarks_folder.format(name=self.name))

    @property
    def id(self):
        return self._user.id

    @property
    def account(self):
        return self._user.account

    @property
    def name(self):
        return self._user.name
