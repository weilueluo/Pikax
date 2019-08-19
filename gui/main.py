from tkinter import *

from login import LoginScreen
from pikaxhandler import PikaxHandler

root = Tk()
root.geometry('600x400')
root.title('Pikax - Pixiv Downloader')
root.protocol("WM_DELETE_WINDOW", root.destroy)


# restorecyclebin@gmail.com


def main():
    login_screen = LoginScreen(master=root, pikax_handler=PikaxHandler())
    root.mainloop()


if __name__ == '__main__':
    main()
