from .api.artwork import Illust
from .api.models import BaseIDProcessor

__all__ = ['DefaultIDProcessor']


class DefaultIDProcessor(BaseIDProcessor):

    def __init__(self):
        super().__init__()

    def process_mangas(self, ids):
        # they are essentially the same, just illust with more pages
        return self.process_illusts(ids)

    def process_illusts(self, ids):
        return self._general_processor(Illust, ids)
