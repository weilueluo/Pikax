import enum
from enum import Enum
from typing import List, Dict, Tuple
from .. import params


class UserInterface:

    def bookmarks(self, limit: int) -> List[int]: raise NotImplementedError

    def illusts(self, limit: int) -> List[int]: raise NotImplementedError

    def novels(self, limit: int) -> List[int]: raise NotImplementedError

    def mangas(self, limit: int) -> List[int]: raise NotImplementedError


class PagesInterface:

    def search(self, limit: int) -> List[int]: raise NotImplementedError

    def rank(self, limit: int) -> List[int]: raise NotImplementedError


class Artwork:

    @property
    def bookmarks(self): raise NotImplementedError

    @property
    def views(self): raise NotImplementedError

    @property
    def author(self): raise NotImplementedError

    @property
    def title(self): raise NotImplementedError

    @property
    def likes(self): raise NotImplementedError

    class DownloadStatus(enum.Enum):
        OK = 'OK'
        SKIPPED = 'skipped'
        FAILED = 'failed'

    # return download status, content, filename
    def __getitem__(self, index): raise NotImplementedError

    # return num of pages
    def __len__(self): raise NotImplementedError

    # set variables, raises ReqException
    def config(self): raise NotImplementedError


class IDProcessorInterface:

    def __init__(self):
        self.type_to_function = {
            params.NOVEL: self.process_novels,
            params.MANGA: self.process_mangas,
            params.ILLUST: self.process_illusts,
            params.GIF: self.process_gifs
        }

    def process_illusts(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]: raise NotImplementedError

    def process_novels(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]: raise NotImplementedError

    def process_gifs(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]: raise NotImplementedError

    def process_mangas(self, ids: List[int]) -> Tuple[List[Artwork], List[int]]: raise NotImplementedError

    def process(self, ids: List[int], process_type: params.Type) -> Tuple[List[Artwork], List[int]]:
        if process_type not in [params.ILLUST, params.NOVEL, params.MANGA, params.GIF]:
            from ..exceptions import ProcessError
            raise ProcessError(f'Process type:{process_type} is not valid, should be in '
                               f'{[params.ILLUST, params.NOVEL, params.MANGA, params.GIF]}')

        return self.type_to_function[process_type](ids)
