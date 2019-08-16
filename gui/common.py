import sys
from tkinter import END, NORMAL, DISABLED, Text, CENTER


def go_to_next_screen(src, dest):
    pikax_handler = src.pikax_handler
    master = src.frame.master
    src.destroy()
    dest(master, pikax_handler)


class StdoutRedirector:
    def __init__(self, text_component):
        self.text_component = text_component

    def write(self, string):
        self.text_component.configure(state=NORMAL)
        self.text_component.insert(END, string)
        if isinstance(self.text_component, Text):
            self.text_component.see(END)
        self.text_component.configure(state=DISABLED)

    def flush(self):
        pass
