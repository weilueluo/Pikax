import sys
from tkinter import END, NORMAL, DISABLED, Text, CENTER, Entry


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

        if isinstance(self.text_component, Text):
            self.text_component.delete(1.0, END)
            self.text_component.insert(1.0, string)
            self.text_component.see(END)
        elif isinstance(self.text_component, Entry):
            self.text_component.delete(0, END)
            self.text_component.insert(0, string)
        else:
            raise TypeError('Not text or entry')
        self.text_component.configure(state=DISABLED)

    def flush(self):
        pass
