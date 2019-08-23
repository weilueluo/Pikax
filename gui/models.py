from factory import *


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

    def make_button(self, text=''):
        return make_button(self.frame, text=text)

    def make_label(self, text=''):
        return make_label(self.frame, text=text)

    def make_frame(self):
        return make_frame(self.frame)

    def make_dropdown(self, default, choices):
        return make_dropdown(self.frame, default, choices)

    def make_entry(self):
        return make_entry(self.frame)

    def make_download_output(self):
        text = make_text(self.frame)
        text.configure(height=6, state=DISABLED)
        return text

    def grid(self, component):
        grid(component)

    def pack(self, component):
        pack(component)

    def redirect_output_to(self, text_component):
        import sys
        from common import StdoutRedirector
        sys.stdout = StdoutRedirector(text_component)
