import os
import pickle
import sys
import threading
import tkinter as tk
from multiprocessing import Process
from tkinter import END, NORMAL, DISABLED, Text, Entry, TclError

import settings

_screen_lock = threading.Lock()


def go_to_next_screen(src, dest):
    global _screen_lock
    if _screen_lock.locked():
        return
    with _screen_lock:
        pikax_handler = src.pikax_handler
        master = src.frame.master
        dest(master, pikax_handler)
        src.destroy()  # destroy after creation to prevent black screen in the middle


def download(target, args=(), kwargs=()):
    from download import DownloadWindow
    Process(target=DownloadWindow, args=(target, args, kwargs)).start()


def remove_invalid_chars(string):
    return ''.join([s if ord(s) < 65565 else '#' for s in str(string)])


class StdoutTextWidgetRedirector:
    def __init__(self, text_component):
        self.text_component = text_component
        self.text_component.tag_configure('center', justify=tk.CENTER)

    def write(self, string, append=False):
        try:
            string = remove_invalid_chars(string)
            self.text_component.configure(state=NORMAL)

            if isinstance(self.text_component, Text):
                if append:
                    self.text_component.insert(END, '\n' + string)
                else:
                    self.text_component.delete(1.0, END)
                    self.text_component.insert(1.0, string, 'center')
                self.text_component.see(END)
            elif isinstance(self.text_component, Entry):
                self.text_component.delete(0, END)
                self.text_component.insert(0, string)
            else:
                raise TypeError('Not text or entry')
            self.text_component.configure(state=DISABLED)
        except TclError as e:  # should not happen
            sys.stderr.write(str(e))

    def flush(self):
        pass


class StdoutCanvasTextRedirector:
    def __init__(self, canvas, text_id):
        self.text_id = text_id
        self.canvas = canvas

    def write(self, string):
        try:
            self.canvas.itemconfigure(self.text_id, text=remove_invalid_chars(string))
        except TclError as e:
            self.canvas.itemconfigure(self.text_id, text=remove_invalid_chars(str(e)))

    def flush(self):
        pass


def crop_to_dimension(im, width_ratio, height_ratio, focus=tk.CENTER):
    transformed_width = im.height / height_ratio * width_ratio
    if transformed_width < im.width:
        width = transformed_width
        height = im.height
    else:
        height = im.width / width_ratio * height_ratio
        width = im.width

    mid = list(x / 2 for x in im.size)
    half_width = width / 2
    half_height = height / 2

    if focus == tk.CENTER:
        mid = mid
    elif focus == tk.N:
        mid[1] = half_height
    elif focus == tk.S:
        mid[1] = im.size[1] - half_height
    elif focus == tk.W:
        mid[0] = half_width
    elif focus == tk.E:
        mid[0] = im.size[0] - half_width
    else:
        raise ValueError(f'Invalid focus: {focus}')

    left = mid[0] - half_width
    upper = mid[1] - half_height
    right = mid[0] + half_width
    lower = mid[1] + half_height

    return im.crop((left, upper, right, lower))


def get_background_file_path():
    import os
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, settings.CANVAS_BACKGROUND_PATH)


# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def config_root(root, title, width, height):
    root.geometry('{}x{}'.format(width, height))
    root.configure(borderwidth=0, highlightthickness=0)
    root.title(title)
    root.resizable(False, False)
    center(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)


def save_to_local(file_path, item):
    with open(file_path, 'wb') as file:
        pickle.dump(item, file, pickle.HIGHEST_PROTOCOL)


def load_from_local(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)


def remove_local_file(file_path):
    os.remove(file_path)
