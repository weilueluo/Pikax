import unittest

from pikax import LoginHandler, settings, DefaultIDProcessor, params


class IDProcessorTest(unittest.TestCase):
    def setUp(self) -> None:
        status, self.client = LoginHandler(settings.username, settings.password).android_login()
        if status is not LoginHandler.LoginStatus.ANDROID:
            self.fail(f'Set up client failed: {status}')
        self.processor = DefaultIDProcessor()

    def test_process1(self):
        ids = self.client.rank(limit=17)
        successes, failed = self.processor.process(ids, params.ProcessType.ILLUST)
        self.assertEqual(len(successes), 17)
        self.assertEqual(len(failed), 0)

    def test_process2(self):
        ids = self.client.search(keyword='arknights', search_type=params.SearchType.ILLUST_OR_MANGA, limit=21)
        successes, fails = self.processor.process(ids, params.ProcessType.ILLUST)
        self.assertEqual(len(successes), 21)
        self.assertEqual(len(fails), 0)


if __name__ == '__main__':
    unittest.main()
