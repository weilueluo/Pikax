
from threading import Thread

import settings
from models import PikaxGuiComponent


class DownloadThread(Thread):

    def __init__(self, target, args=(), kwargs=(), output_area=None, button=None):
        super().__init__(target=target, args=args, kwargs=kwargs)
        self.output_area = output_area
        self.button = button

    def run(self):
        super().run()
        self.button.configure(text='done')
        if self.output_area:
            self.output_area.see(0.0)


class DownloadWindow(PikaxGuiComponent):

    def __init__(self, target, args=(), kwargs=()):
        import tkinter as tk
        self.window = tk.Tk()
        self.window.geometry(settings.DOWNLOAD_WINDOW_SIZE)
        self.window.title(settings.PIKAX_DOWNLOADER_TITLE)
        super().__init__(self.window, pikax_handler=None)

        self.cancel_button = self.make_button(text='cancel')
        self.cancel_button.configure(command=self.cancel_clicked)
        self.display_area = self.make_download_output()
        self.redirect_output_to(self.display_area)

        self.components = [
            self.display_area,
            self.cancel_button
        ]

        self.buttons = [
            self.cancel_button
        ]

        self.download_thread = DownloadThread(target=target, args=args, kwargs=kwargs, output_area=self.display_area,
                                              button=self.cancel_button)
        self.load()

    def cancel_clicked(self):
        self.destroy()

    def make_download_output(self):
        text_area = self.make_text()
        text_area.configure(height=20)
        return text_area

    def load(self):
        import tkinter as tk
        for index, component in enumerate(self.components):
            component.grid_configure(row=index)
            self.grid(component)

        for button in self.buttons:
            button.configure(state=tk.NORMAL)

        self.pack(self.frame)

        self.window.grab_set()
        self.download_thread.start()
        self.window.mainloop()

    def destroy(self):
        self.window.destroy()
