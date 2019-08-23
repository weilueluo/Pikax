from tkinter import *

import settings
from login import LoginScreen
from pikaxhandler import PikaxHandler


# restorecyclebin@gmail.com

# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def main():
    root = Tk()
    root.geometry(settings.MAIN_WINDOW_SIZE)
    root.title(settings.PIKAX_DOWNLOADER_TITLE)
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    center(root)
    LoginScreen(master=root, pikax_handler=PikaxHandler())
    root.mainloop()


if __name__ == '__main__':
    main()
