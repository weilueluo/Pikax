import multiprocessing
import tkinter as tk

import settings
import texts
from common import config_root
from login import LoginScreen
from pikaxhandler import PikaxHandler


# restorecyclebin@gmail.com

def main():
    root = tk.Tk()
    config_root(root=root, title=texts.get('FRAME_TITLE'), width=settings.MAIN_WINDOW_WIDTH,
                height=settings.MAIN_WINDOW_HEIGHT)
    LoginScreen(master=root, pikax_handler=PikaxHandler())
    root.mainloop()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
