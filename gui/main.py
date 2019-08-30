import multiprocessing
from tkinter import *

import settings
from login import LoginScreen
from pikaxhandler import PikaxHandler
from common import center


# restorecyclebin@gmail.com

def main():
    root = Tk()
    root.geometry('{}x{}'.format(settings.MAIN_WINDOW_WIDTH, settings.MAIN_WINDOW_HEIGHT))
    root.configure(borderwidth=0, highlightthickness=0)
    root.title(settings.PIKAX_DOWNLOADER_TITLE)
    root.resizable(False, False)
    center(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    LoginScreen(master=root, pikax_handler=PikaxHandler())
    root.mainloop()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
