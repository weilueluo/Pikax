import glob
import re
import sys
import tkinter as tk
from multiprocessing import Process
from tkinter import END, NORMAL, DISABLED, Text, Entry, TclError

import settings


def go_to_next_screen(src, dest):
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

    def write(self, string, append=False):
        try:
            string = remove_invalid_chars(string)
            self.text_component.configure(state=NORMAL)

            if isinstance(self.text_component, Text):
                if append:
                    self.text_component.insert(END, '\n' + string)
                else:
                    self.text_component.delete(1.0, END)
                    self.text_component.insert(1.0, string)
                self.text_component.tag_configure('center', justify=tk.CENTER)
                self.text_component.tag_add('center', 1.0, tk.END)
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
            string = remove_invalid_chars(string)
            self.canvas.itemconfigure(self.text_id, text=string)
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
    for file in glob.glob(settings.IMAGES_PATH):
        if re.search(settings.CANVAS_BACKGROUND_PATH, file):
            return file
    return None
