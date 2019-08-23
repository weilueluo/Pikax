import sys
from multiprocessing import Process
from tkinter import END, NORMAL, DISABLED, Text, Entry, TclError

from download import DownloadWindow


def go_to_next_screen(src, dest):
    pikax_handler = src.pikax_handler
    master = src.frame.master
    src.destroy()
    dest(master, pikax_handler)


def download(target, args=(), kwargs=()):
    Process(target=DownloadWindow, args=(target, args, kwargs)).start()


class StdoutRedirector:
    def __init__(self, text_component):
        self.text_component = text_component

    def write(self, string, append=False):
        try:
            string = ''.join([s if ord(s) < 65565 else '#' for s in str(string)])
            self.text_component.configure(state=NORMAL)

            if isinstance(self.text_component, Text):
                if append:
                    self.text_component.insert(END, '\n' + string)
                else:
                    self.text_component.delete(1.0, END)
                    self.text_component.insert(1.0, string)
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
