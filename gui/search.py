import os
import sys

from common import go_to_next_screen, StdoutTextWidgetRedirector, download
from download import DownloadWindow
from factory import NORMAL, grid, pack, DISABLED
from lib.pikax.util import clean_filename
from menu import MenuScreen
from models import PikaxGuiComponent


class SearchScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        # labels
        self.keyword_label = self.make_label(text='keyword')
        self.match_label = self.make_label(text='tag match')
        self.sort_label = self.make_label(text='sort')
        self.popularity_label = self.make_label(text='popularity')
        self.limit_label = self.make_label(text='limit')
        self.download_folder_label = self.make_label(text='download folder')

        self.labels = [
            self.keyword_label,
            self.limit_label,
            self.match_label,
            self.sort_label,
            self.popularity_label,
            self.download_folder_label
        ]

        # inputs
        self.keyword_entry = self.make_entry()
        self.limit_entry = self.make_entry()
        match_choices = ['exact', 'partial', 'any']
        self.match_dropdown = self.make_dropdown('partial', match_choices)
        sort_choices = ['date ascending', 'date descending']
        self.sort_dropdown = self.make_dropdown('date descending', sort_choices)
        popularity_choices = ['any', '100', '500', '1000', '5000', '10000', '20000']
        self.popularity_dropdown = self.make_dropdown('any', popularity_choices)
        self.download_folder_entry = self.make_entry()

        self.inputs = [
            self.keyword_entry,
            self.limit_entry,
            self.match_dropdown,
            self.sort_dropdown,
            self.popularity_dropdown,
            self.download_folder_entry
        ]

        # buttons
        self.search_and_download_button = self.make_button(text='search and download')
        self.search_and_download_button.configure(command=self.search_and_download_clicked)
        self.back_button = self.make_button(text='back')
        self.back_button.configure(command=self.back_clicked)

        for widget in self.frame.children.values():
            widget.bind('<Return>', self.search_and_download_clicked)

        self.load()

    def load(self):
        # labels
        for index, label in enumerate(self.labels):
            label.grid_configure(row=index)
            self.grid(label)

        # inputs
        for index, input in enumerate(self.inputs):
            input.grid_configure(row=index, column=1)
            self.grid(input)

        # buttons
        self.back_button.grid_configure(row=6, column=0)
        self.back_button.configure(state=NORMAL)
        self.search_and_download_button.grid_configure(row=6, column=1)
        self.search_and_download_button.configure(state=NORMAL)

        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

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
