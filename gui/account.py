from common import make_readable_from_unreadable, make_unreadable_when_serialized


class Account:
    def __init__(self, username, password):
        self._username = make_unreadable_when_serialized(username)
        self._password = make_unreadable_when_serialized(password)

    @property
    def username(self):
        return ''.join(make_readable_from_unreadable(self._username))

    @property
    def password(self):
        return ''.join(make_readable_from_unreadable(self._password))


def main():
    acc = Account('username', 'password')
    print(acc.username)
    print(acc.password)


if __name__ == '__main__':
    main()
