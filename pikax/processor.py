from .api.artwork import Illust
from .api.models import BaseIDProcessor


class DefaultIDProcessor(BaseIDProcessor):

    def __init__(self):
        super().__init__()

    def process_mangas(self, ids):
        # they are essentially the same, just illust with more pages
        return self.process_illusts(ids)

    def process_illusts(self, ids):
        return self._general_processor(Illust, ids)


def test():
    from . import settings
    from .items import LoginHandler
    from . import params
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print('Testing Processor')
    status, client = LoginHandler(settings.username, settings.password).login()
    print(status, client)
    processor = DefaultIDProcessor()
    ids = client.rank(limit=100)
    successes, failed = processor.process(ids, params.ProcessType.ILLUST)
    assert len(successes) == 100, len(successes)

    ids = client.search(keyword='arknights', search_type=params.SearchType.ILLUST_OR_MANGA, limit=50)
    successes, fails = processor.process(ids, params.ProcessType.ILLUST)
    assert len(successes) == 50, len(successes)

    print('Successfully tested processor')


def main():
    test()


if __name__ == '__main__':
    main()
