from tkinter import *

from login import LoginScreen
from pikaxhandler import PikaxHandler

root = Tk()
root.geometry('600x400')
root.title('Pikax - Pixiv Downloader')
root.protocol("WM_DELETE_WINDOW", root.destroy)


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
    center(root)
    LoginScreen(master=root, pikax_handler=PikaxHandler())
    root.mainloop()


if __name__ == '__main__':
    main()
