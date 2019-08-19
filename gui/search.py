import os
import sys

from common import go_to_next_screen, StdoutRedirector
from factory import make_label, make_entry, make_button, make_dropdown, NORMAL, grid, pack, DISABLED, make_text
from lib.pikax.util import clean_filename
from menu import MenuScreen
from models import PikaxGuiComponent


class SearchScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.keyword_label = make_label(self.frame, text='keyword')
        self.match_label = make_label(self.frame, text='tag match')
        self.sort_label = make_label(self.frame, text='sort')
        self.popularity_label = make_label(self.frame, text='popularity')
        self.limit_label = make_label(self.frame, text='limit')

        self.keyword_entry = make_entry(self.frame)
        self.limit_entry = make_entry(self.frame)

        self.sort_choices = ['date ascending', 'date descending']
        self.sort_dropdown = make_dropdown(self.frame, 'date descending', self.sort_choices)

        self.popularity_choices = ['any', '100', '500', '1000', '5000', '10000', '20000']
        self.popularity_dropdown = make_dropdown(self.frame, 'any', self.popularity_choices)

        self.match_choices = ['exact', 'partial', 'any']
        self.match_dropdown = make_dropdown(self.frame, 'partial', self.match_choices)

        self.folder_label = make_label(self.frame, text='download folder')
        self.folder_entry = make_entry(self.frame)

        self.search_and_download_button = make_button(self.frame, text='search and download')
        self.search_and_download_button.configure(command=self.search_and_download_clicked)
        self.back_button = make_button(self.frame, text='back')
        self.back_button.configure(command=self.back_clicked)

        self.output_text = make_text(self.frame)
        self.output_text.configure(state=DISABLED, height=6)
        sys.stdout = StdoutRedirector(self.output_text)

        self.load()

    def load(self):
        self.keyword_label.grid_configure(row=0)
        self.limit_label.grid_configure(row=1)
        self.sort_label.grid_configure(row=2)
        self.popularity_label.grid_configure(row=3)
        self.match_label.grid_configure(row=4)
        self.folder_label.grid_configure(row=5)

        self.keyword_entry.grid_configure(row=0, column=1)
        self.limit_entry.grid_configure(row=1, column=1)
        self.sort_dropdown.grid_configure(row=2, column=1)
        self.popularity_dropdown.grid_configure(row=3, column=1)
        self.match_dropdown.grid_configure(row=4, column=1)
        self.folder_entry.grid_configure(row=5, column=1)

        self.back_button.grid_configure(row=6, column=0)
        self.back_button.configure(state=NORMAL)

        self.search_and_download_button.grid_configure(row=6, column=1)
        self.search_and_download_button.configure(state=NORMAL)

        self.output_text.grid_configure(row=7, columnspan=2)

        self.frame.pack_configure(expand=True)

        grid(self.keyword_label)
        grid(self.keyword_entry)
        grid(self.match_label)
        grid(self.match_dropdown)
        grid(self.limit_label)
        grid(self.limit_entry)
        grid(self.folder_label)
        grid(self.folder_entry)
        grid(self.popularity_label)
        grid(self.popularity_dropdown)
        grid(self.sort_label)
        grid(self.sort_dropdown)
        grid(self.output_text)

        pack(self.frame)

    def destroy(self):
        self.frame.destroy()

    def back_clicked(self):
        go_to_next_screen(src=self, dest=MenuScreen)

    def search_and_download_clicked(self):
        try:
            keyword = str(self.keyword_entry.get())
            if not keyword:
                raise ValueError('Keyword cannot be empty')

            folder_input = str(self.folder_entry.get())
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

        import threading
        params['keyword'] = keyword
        params['folder'] = folder
        download_thread = threading.Thread(target=self.pikax_handler.search, kwargs=params)
        download_thread.start()

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
