import os
import sys
import tkinter as tk

from common import go_to_next_screen, download
from lib.pikax.util import clean_filename
from menu import MenuScreen
from models import PikaxGuiComponent


class SearchScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        self.grid_height = 10
        self.grid_width = 15

        # labels
        self.keyword_text_id = self.add_text(text='keyword', column=5, row=1)
        self.match_text_id = self.add_text(text='tag match', column=5, row=2)
        self.sort_text_id = self.add_text(text='sort', column=5, row=3)
        self.popularity_text_id = self.add_text(text='popularity', column=5, row=4)
        self.limit_text_id = self.add_text(text='limit', column=5, row=5)
        self.download_folder_text_id = self.add_text(text='download folder', column=5, row=6)

        # create inputs
        self.keyword_entry = self.make_entry()
        self.limit_entry = self.make_entry()
        match_choices = ['exact', 'partial', 'any']
        self.match_dropdown = self.make_dropdown('partial', match_choices)
        sort_choices = ['date ascending', 'date descending']
        self.sort_dropdown = self.make_dropdown('date descending', sort_choices)
        popularity_choices = ['any', '100', '500', '1000', '5000', '10000', '20000']
        self.popularity_dropdown = self.make_dropdown('any', popularity_choices)
        self.download_folder_entry = self.make_entry()

        # add inputs
        self.keyword_entry_id = self.add_widget(widget=self.keyword_entry, column=9, row=1)
        self.limit_entry_id = self.add_widget(widget=self.limit_entry, column=9, row=2)
        self.match_dropdown_id = self.add_widget(widget=self.match_dropdown, column=9, row=3)
        self.sort_dropdown_id = self.add_widget(widget=self.sort_dropdown, column=9, row=4)
        self.popularity_dropdown_id = self.add_widget(widget=self.popularity_dropdown, column=9, row=5)
        self.download_folder_entry = self.add_widget(widget=self.download_folder_entry, column=9, row=6)

        # create buttons
        self.search_and_download_button = self.make_button(text='download')
        self.back_button = self.make_button(text='back')

        # add buttons
        self.back_button_id = self.add_widget(widget=self.back_button, column=5, row=7)
        self.search_and_download_button_id = self.add_widget(self.search_and_download_button, column=9, row=7)

        # config
        self.config_buttons()
        for widget in self.frame.children.values():
            widget.bind('<Return>', self.search_and_download_clicked)
        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

    def config_buttons(self):
        self.search_and_download_button.configure(command=self.search_and_download_clicked)
        self.back_button.configure(command=self.back_clicked)

    def destroy(self):
        self.frame.destroy()

    def back_clicked(self):
        go_to_next_screen(src=self, dest=MenuScreen)

    def search_and_download_clicked(self):
        try:
            keyword = str(self.keyword_entry.get())
            if not keyword:
                raise ValueError('Keyword cannot be empty')

            folder_input = str(self.download_folder_entry.get())
            if folder_input != clean_filename(folder_input):
                raise ValueError('Folder name contains invalid characters')
            folder = folder_input or None

            try:
                limit_input = int(self.limit_entry.get()) if self.limit_entry.get() else None
            except ValueError:
                raise ValueError('Limit must be a integer or empty')
            match_input = str(self.match_dropdown.get())
            sort_input = str(self.sort_dropdown.get())
            popularity_input = str(self.popularity_dropdown.get())
            params = self.check_inputs(limit_input=limit_input, match_input=match_input, sort_input=sort_input,
                                       popularity_input=popularity_input)
        except (TypeError, ValueError) as e:
            sys.stdout.write('Please check your inputs' + os.linesep + f'Error Message: {e}')
            return

        params['keyword'] = keyword
        params['folder'] = folder
        download(target=self.pikax_handler.search, kwargs=params)

    @staticmethod
    def check_inputs(limit_input, match_input, sort_input, popularity_input):
        from lib.pikax import params

        if not limit_input or limit_input == 'any':
            limit = None
        else:
            limit = int(limit_input)

        if not match_input or match_input == 'any':
            match = params.Match.ANY
        elif match_input == 'exact':
            match = params.Match.EXACT
        else:
            match = params.Match.PARTIAL

        if not sort_input or sort_input == 'date descending':
            sort = params.Sort.DATE_DESC
        else:
            sort = params.Sort.DATE_ASC

        if not popularity_input or popularity_input == 'any':
            popularity = None
        else:
            popularity = int(popularity_input)

        return {
            'limit': limit,
            'sort': sort,
            'match': match,
            'popularity': popularity
        }


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()
    SearchScreen(root, None)
    root.mainloop()
