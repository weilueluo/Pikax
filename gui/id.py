import re
import sys
from threading import Thread

from common import go_to_next_screen
from models import PikaxGuiComponent
import tkinter as tk


class IDDownloadThread(Thread):
    def __init__(self, output_area, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_area = output_area

    def run(self):
        super().run()
        if self.output_area:
            self.output_area.see(0.0)


class IdScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        self.grid_width = 20
        self.grid_height = 9
        self.id_or_url_text_id = self.add_text(text='Illustration id or url', row=2, column=9, columnspan=2)

        self.id_or_url_entry = self.make_entry(width=40)
        self.url_or_entry_id = self.add_widget(widget=self.id_or_url_entry, row=3, column=9, columnspan=2)

        # buttons
        self.download_button = self.make_button(text='download')
        self.download_button_id = self.add_widget(widget=self.download_button, row=4, column=11)
        self.back_button = self.make_button(text='back')
        self.back_button_id = self.add_widget(widget=self.back_button, row=4, column=8)

        self.download_output = self.make_download_output()
        self.download_output_id = self.add_widget(widget=self.download_output, row=6, column=9, columnspan=2)
        self.redirect_output_to(self.download_output)

        self.download_button.configure(command=self.download_clicked)
        self.back_button.configure(command=self.back_clicked)

        self.download_thread = None

        self.id_or_url_entry.focus_set()
        self.download_output.configure(state=tk.DISABLED)
        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

    def back_clicked(self):
        from menu import MenuScreen
        go_to_next_screen(self, MenuScreen)

    def download_clicked(self):
        user_input = self.id_or_url_entry.get()
        search_id = re.search(r'(?<!\d)\d{8}(?!\d)', user_input, re.S)
        if search_id:
            self.download_thread = IDDownloadThread(output_area=self.download_output, target=self.pikax_handler.download_by_id,
                                                    args=(search_id.group(0),))
            self.download_thread.start()
        else:
            if re.search(r'\d{8}', user_input, re.S):
                sys.stdout.write('Ambiguous ID found, ID should be 8 digits only')
            else:
                sys.stdout.write('No ID found in input')

    def destroy(self):
        self.frame.destroy()
