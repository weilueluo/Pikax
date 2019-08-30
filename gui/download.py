import tkinter as tk
from threading import Thread
from tkinter import font

import settings
from common import center
from models import PikaxGuiComponent


class DownloadThread(Thread):

    def __init__(self, target, args=(), kwargs=(), output_area=None, button=None):
        super().__init__(target=target, args=args, kwargs=kwargs)
        self.output_area = output_area
        self.button = button

    def run(self):
        super().run()
        self.button.configure(text='done')
        if isinstance(self.output_area, tk.Text):
            self.output_area.see(0.0)


# this class should be run in a different process
class DownloadWindow(PikaxGuiComponent):

    def __init__(self, target, args=(), kwargs=()):
        self.window = tk.Tk()
        self.width = settings.DOWNLOAD_WINDOW_WIDTH
        self.height = settings.DOWNLOAD_WINDOW_HEIGHT
        self.window.geometry('{}x{}'.format(self.width, self.height))
        self.window.title(settings.PIKAX_DOWNLOADER_TITLE)
        self.window.resizable(False, False)
        center(self.window)
        super().__init__(self.window, pikax_handler=None)

        self.grid_width = 3
        # add using the old grid height so that report button and cancel button are on the same height
        self.cancel_button = self.make_button(text='cancel')
        self.cancel_button_id = self.add_widget(widget=self.cancel_button, column=1, row=self.grid_height - 30)

        self.grid_height = 9
        self.text_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=settings.DEFAULT_FONT_SIZE - 2)
        self.display_area_height = 16
        self.display_area_width = 75

        self.display_area = self.make_text()
        self.display_area_id = self.add_widget(widget=self.display_area, row=4, column=0, columnspan=3)

        # configure
        self.config()
        self.pack(self.frame)
        self.window.grab_set()
        self.download_thread = DownloadThread(target=target, args=args, kwargs=kwargs, output_area=self.display_area,
                                              button=self.cancel_button)
        self.download_thread.start()
        self.window.mainloop()

    def config(self):
        self.cancel_button.configure(command=self.cancel_clicked)
        self.display_area.configure(height=self.display_area_height, width=self.display_area_width)
        self.redirect_output_to(self.display_area)

    def cancel_clicked(self):
        self.window.destroy()
