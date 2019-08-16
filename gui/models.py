from tkinter import Frame


class PikaxGuiComponent:

    def __init__(self, master, pikax_handler):
        self._frame = Frame(master)
        self._pikax_handler = pikax_handler

    def load(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    @property
    def frame(self):
        return self._frame

    @property
    def pikax_handler(self):
        return self._pikax_handler
