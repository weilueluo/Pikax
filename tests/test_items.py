import unittest

from pikax import LoginHandler, settings, AndroidAPIClient, DefaultAPIClient


class LoginHandlerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.login_handler = LoginHandler(settings.username, settings.password)

    def test_android_login_success(self):
        status, client = self.login_handler.android_login()
        self.assertEqual(status, LoginHandler.LoginStatus.ANDROID)
        self.assertTrue(isinstance(client, AndroidAPIClient))

    def test_android_login_failed(self):
        status, client = self.login_handler.android_login('invalid_username', 'invalid_password')
        self.assertEqual(status, LoginHandler.LoginStatus.LOG_OUT)
        self.assertTrue(isinstance(client, DefaultAPIClient))


if __name__ == '__main__':
    unittest.main()
