import tkinter as tk
from threading import Thread
from tkinter import font

import settings
import texts
import pikax
from common import config_root
from models import PikaxGuiComponent


class DownloadThread(Thread):

    def __init__(self, target, args=(), kwargs=(), output_area=None, button=None, end_height=None):
        super().__init__(target=target, args=args, kwargs=kwargs)
        self.output_area = output_area
        self.button = button
        self.end_height = end_height

    def run(self):
        super().run()
        self.button.configure(text=texts.get('DOWNLOADER_DONE'))
        if isinstance(self.output_area, tk.Text):
            self.output_area.see(0.0)
            if self.end_height:
                self.output_area.configure(height=int(self.end_height))


# instance of this class should be created in a different process
class DownloadWindow(PikaxGuiComponent):

    def __init__(self, target, args=None, kwargs=None):
        if kwargs is None:
            kwargs = dict()
        import texts
        if kwargs:
            texts.set_lang(kwargs['lang'])
            del kwargs['lang']
        self.window = tk.Tk()
        self.width = settings.DOWNLOAD_WINDOW_WIDTH
        self.height = settings.DOWNLOAD_WINDOW_HEIGHT
        config_root(root=self.window, title=texts.get('FRAME_TITLE'), width=self.width, height=self.height)

        super().__init__(self.window, pikax_handler=None)

        self.grid_width = 3
        # add using the old grid height so that report button and cancel button are on the same height
        self.cancel_button = self.make_button(text=texts.get('DOWNLOADER_CANCEL'))
        self.cancel_button_id = self.add_widget(widget=self.cancel_button, column=1, row=self.grid_height - 30)

        self.grid_height = 9
        self.text_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)
        self.display_area_height = 7
        self.end_display_area_height = 14
        self.display_area_width = 75

        self.display_area = self.make_text()
        self.display_area_id = self.add_widget(widget=self.display_area, row=4, column=0, columnspan=3)

        # configure
        # remove language button, not in use
        self.language_button.destroy()
        self.config()
        self.grid(self.frame)
        self.window.grab_set()
        self.download_thread = DownloadThread(target=target, args=args, kwargs=kwargs, output_area=self.display_area,
                                              button=self.cancel_button, end_height=self.end_display_area_height)
        self.download_thread.start()
        self.window.mainloop()

    def config(self):
        self.cancel_button.configure(command=self.cancel_clicked)
        self.display_area.configure(height=self.display_area_height, width=self.display_area_width)
        self.redirect_output_to(self.display_area, preprocess_func=self.preprocess_text)

    @staticmethod
    def preprocess_text(string):
        # the information are assumed to be separated by |
        string = '\n'.join(string.split('|'))  # the text widget uses \n as line separator
        return string

    def cancel_clicked(self):
        self.window.destroy()
