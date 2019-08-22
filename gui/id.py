import re
import sys
from threading import Thread
from tkinter import NORMAL, W, E

from models import PikaxGuiComponent
from common import go_to_next_screen


class IdScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.id_or_url_label = self.make_label('Id or illustration url here')
        self.id_or_url_entry = self.make_entry()
        self.download_button = self.make_button(text='download')
        self.download_output = self.make_download_output()
        self.back_button = self.make_button('back')

        self.components = [
            self.id_or_url_label,
            self.id_or_url_entry,
            self.download_button,
            self.download_output
        ]

        self.download_button.configure(command=self.download_clicked)
        self.back_button.configure(command=self.back_clicked)
        self.redirect_output_to(self.download_output)

        self.load()

    def back_clicked(self):
        from menu import MenuScreen
        go_to_next_screen(self, MenuScreen)

    def download_clicked(self):
        user_input = self.id_or_url_entry.get()
        search_id = re.search(r'(?<!\d)\d{8}(?!\d)', user_input, re.S)
        if search_id:
            Thread(target=self.pikax_handler.download_by_id, args=(search_id.group(0),)).start()
        else:
            if re.search(r'\d{8}', user_input, re.S):
                sys.stdout.write('Ambiguous Id found, id should be 8 digits')
            else:
                sys.stdout.write('No id found in input')

    def load(self):
        for index, component in enumerate(self.components):
            component.grid_configure(row=index, columnspan=2)

        self.back_button.grid_configure(row=len(self.components) - 2, sticky=E, columnspan=1)
        self.download_button.grid_configure(row=len(self.components) - 2, column=1, sticky=W, columnspan=1)

        for component in self.components:
            self.grid(component)

        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

        self.download_button.configure(state=NORMAL)
        self.back_button.configure(state=NORMAL)

    def destroy(self):
        self.frame.destroy()
