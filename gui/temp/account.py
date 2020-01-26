import texts
from common import make_readable_from_unreadable, make_unreadable_when_serialized


class Account:
    def __init__(self, username, password):
        self._username = make_unreadable_when_serialized(username)
        self._password = make_unreadable_when_serialized(password)

    @property
    def username(self):
        try:
            return make_readable_from_unreadable(self._username)
        except ValueError:
            raise AttributeError(texts.get('ACCOUNT_USERNAME_CORRUPTED'))

    @property
    def password(self):
        try:
            return make_readable_from_unreadable(self._password)
        except ValueError:
            raise AttributeError(texts.get('ACCOUNT_PASSWORD_CORRUPTED'))


def main():
    acc = Account('username', 'password')
    print(acc.username)
    print(acc.password)


if __name__ == '__main__':
    main()
