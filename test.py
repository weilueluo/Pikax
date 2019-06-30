class A:
    def m(self):
        print('hi')


class A():
    def m(self):
        print('hey')


if __name__ == '__main__':
    o = A()
    o.m()
