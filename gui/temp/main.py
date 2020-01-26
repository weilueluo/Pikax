import multiprocessing
import tkinter as tk

import settings
import texts
from common import config_root, restore_language_if_saved
from login import LoginScreen
from pikaxhandler import PikaxHandler


def restore_data(login_screen):
    new_login_screen = restore_language_if_saved(login_screen)
    if new_login_screen:
        new_login_screen.login_if_credential_exists()


def main():
    root = tk.Tk()
    config_root(root=root, title=texts.get('FRAME_TITLE'), width=settings.MAIN_WINDOW_WIDTH,
                height=settings.MAIN_WINDOW_HEIGHT)
    login_screen = LoginScreen(master=root, pikax_handler=PikaxHandler())
    restore_data(login_screen)
    root.mainloop()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
