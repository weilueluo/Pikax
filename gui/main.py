from tkinter import *

from login import LoginScreen
from pikaxhandler import PikaxHandler

root = Tk()
root.geometry('400x400')
root.title('Pikax - Pixiv Downloader')

pikax_handler = PikaxHandler()


# restorecyclebin@gmail.com


def main():
    login_screen = LoginScreen(master=root, pikax_handler=pikax_handler)
    root.mainloop()


if __name__ == '__main__':
    main()
