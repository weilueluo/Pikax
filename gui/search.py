import os
import sys
import tkinter as tk

import texts
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
        self.keyword_text_id = self.add_text(text=texts.SEARCH_KEYWORD, column=5, row=1)
        self.limit_text_id = self.add_text(text=texts.SEARCH_LIMIT, column=5, row=2)
        self.match_text_id = self.add_text(text=texts.SEARCH_MATCH, column=5, row=3)
        self.sort_text_id = self.add_text(text=texts.SEARCH_SORT, column=5, row=4)
        self.popularity_text_id = self.add_text(text=texts.SEARCH_POPULARITY, column=5, row=5)
        self.download_folder_text_id = self.add_text(text=texts.SEARCH_DOWNLOAD_FOLDER, column=5, row=6)

        # create inputs
        self.keyword_entry = self.make_entry()
        self.limit_entry = self.make_entry()
        self.match_choices = texts.SEARCH_MATCH_CHOICES  # ['exact', 'partial', 'any']
        self.match_dropdown = self.make_dropdown(self.match_choices[1], self.match_choices)
        self.sort_choices = texts.SEARCH_SORT_CHOICES  # ['date ascending', 'date descending']
        self.sort_dropdown = self.make_dropdown(self.sort_choices[1], self.sort_choices)
        # ['any', '100', '500', '1000', '5000', '10000', '20000']
        self.popularity_choices = texts.SEARCH_POPULARITY_CHOICES
        self.popularity_dropdown = self.make_dropdown(self.popularity_choices[0], self.popularity_choices)
        self.download_folder_entry = self.make_entry()

        # add inputs
        self.keyword_entry_id = self.add_widget(widget=self.keyword_entry, column=9, row=1)
        self.limit_entry_id = self.add_widget(widget=self.limit_entry, column=9, row=2)
        self.match_dropdown_id = self.add_widget(widget=self.match_dropdown, column=9, row=3)
        self.sort_dropdown_id = self.add_widget(widget=self.sort_dropdown, column=9, row=4)
        self.popularity_dropdown_id = self.add_widget(widget=self.popularity_dropdown, column=9, row=5)
        self.download_folder_entry_id = self.add_widget(widget=self.download_folder_entry, column=9, row=6)

        # create buttons
        self.search_and_download_button = self.make_button(text=texts.SEARCH_DOWNLOAD)
        self.back_button = self.make_button(text=texts.SEARCH_BACK)

        # add buttons
        self.back_button_id = self.add_widget(widget=self.back_button, column=5, row=7)
        self.search_and_download_button_id = self.add_widget(self.search_and_download_button, column=9, row=7)

        # add output
        self.output_id = self.add_text(text='', row=8, column=7, font=self.output_font)
        self.redirect_output_to(self.output_id, text_widget=False)

        # config
        self.config()

    def config(self):
        inputs = [
            self.keyword_entry,
            self.limit_entry,
            self.match_dropdown,
            self.sort_dropdown,
            self.popularity_dropdown,
            self.download_folder_entry,
        ]
        self.config_buttons()
        for input_widget in inputs:
            input_widget.bind('<Return>', self.search_and_download_clicked)
        self.frame.pack_configure(expand=True)
        self.pack(self.frame)
        inputs[0].focus_set()

    def config_buttons(self):
        self.search_and_download_button.configure(command=self.search_and_download_clicked)
        self.back_button.configure(command=self.back_clicked)

    def destroy(self):
        self.frame.destroy()

    def back_clicked(self):
        go_to_next_screen(src=self, dest=MenuScreen)

    def search_and_download_clicked(self, _=None):
        try:
            keyword = str(self.keyword_entry.get())
            if not keyword:
                raise ValueError(texts.SEARCH_EMPTY_KEYWORD_ERROR)

            folder_input = str(self.download_folder_entry.get())
            if folder_input != clean_filename(folder_input):
                raise ValueError(texts.SEARCH_INVALID_FOLDER_ERROR)
            folder = folder_input or None

            try:
                limit_input = int(self.limit_entry.get()) if self.limit_entry.get() else None
            except ValueError:
                raise ValueError(texts.SEARCH_LIMIT_ERROR)
            match_input = str(self.match_dropdown.get())
            sort_input = str(self.sort_dropdown.get())
            popularity_input = str(self.popularity_dropdown.get())
            params = self.check_inputs(limit_input=limit_input, match_input=match_input, sort_input=sort_input,
                                       popularity_input=popularity_input)
        except (TypeError, ValueError) as e:
            sys.stdout.write(texts.SEARCH_ERROR_MESSAGE.format(error_message=str(e)))
            return

        params['keyword'] = keyword
        params['folder'] = folder
        download(target=self.pikax_handler.search, kwargs=params)

    def check_inputs(self, limit_input, match_input, sort_input, popularity_input):
        from lib.pikax import params
        # ['exact', 'partial', 'any'] match choices
        # ['date ascending', 'date descending'] sort
        # ['any', '100', '500', '1000', '5000', '10000', '20000'] popularity

        if not limit_input or limit_input == self.match_choices[2]:
            limit = None
        else:
            limit = int(limit_input)

        if not match_input or match_input == self.match_choices[2]:
            match = params.Match.ANY
        elif match_input == self.match_choices[0]:
            match = params.Match.EXACT
        else:
            match = params.Match.PARTIAL

        if not sort_input or sort_input == self.sort_choices[1]:
            sort = params.Sort.DATE_DESC
        else:
            sort = params.Sort.DATE_ASC

        if not popularity_input or popularity_input == self.match_choices[2]:
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
