from .models import BaseIDProcessor
from .artwork import Illust, Novel
from ..exceptions import ArtworkError


class DefaultIDProcessor(BaseIDProcessor):

    def __init__(self):
        super().__init__()

    def process_gifs(self, ids):
        raise NotImplementedError('Processing GIF ids is not available in Default ID Processor yet')

    def process_mangas(self, ids):
        # they are essentially the same, just illust with more pages
        return self.process_illusts(ids)

    def process_illusts(self, ids):
        return self._general_processor(Illust, ids)

    def process_novels(self, ids):
        raise NotImplementedError


def test():
    from .. import settings
    from ..v2.items import LoginHandler
    from .. import params
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print('Testing Processor')
    status, client = LoginHandler(settings.username, settings.password).login()
    print(status, client)
    processor = DefaultIDProcessor()
    # ids = client.rank(limit=100)
    # success, failed = processor.process(ids, params.ProcessType.ILLUST)
    # print(len(success))
    # print(len(failed))

    ids = client.search(keyword='arknights', search_type=params.SearchType.NOVEL, limit=50)
    successes, fails = processor.process(ids, params.ProcessType.NOVEL)
    print(successes)
    print(fails)
    print(len(successes))
    print(len(fails))


def main():
    test()


if __name__ == '__main__':
    main()
