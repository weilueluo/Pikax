import re
import sys
from datetime import date
from threading import Thread
from tkinter import NORMAL, DISABLED, END

from common import StdoutRedirector, go_to_next_screen
from factory import make_text, make_entry, make_label, make_button, make_dropdown, grid, pack
from lib.pikax import params
from lib.pikax.util import clean_filename
from models import PikaxGuiComponent


class RankScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.date_label = make_label(self.frame, 'date')
        self.limit_label = make_label(self.frame, 'limit')
        self.type_label = make_label(self.frame, 'type')
        self.content_label = make_label(self.frame, 'content')
        self.download_folder_label = make_label(self.frame, 'download folder')

        self.labels = [
            self.date_label,
            self.limit_label,
            self.type_label,
            self.content_label,
            self.download_folder_label
        ]

        self.back_button = make_button(self.frame, 'back')
        self.download_button = make_button(self.frame, 'rank and download')

        self.date_entry = make_entry(self.frame)
        self.limit_entry = make_entry(self.frame)
        self.download_folder_entry = make_entry(self.frame)

        self.content_types = ['illustration', 'manga']
        self.content_default = self.content_types[0]
        self.content_dropdown = make_dropdown(self.frame, self.content_default, self.content_types)

        self.rank_types = ['daily', 'weekly', 'monthly', 'rookie']
        rank_default = 'daily'
        self.type_dropdown = make_dropdown(self.frame, rank_default, self.rank_types)

        self.inputs = [
            self.date_entry,
            self.limit_entry,
            self.type_dropdown,
            self.content_dropdown,
            self.download_folder_entry
        ]

        self.text_output = make_text(self.frame)
        self.text_output.configure(state=DISABLED, height=6)
        sys.stdout = StdoutRedirector(self.text_output)

        self.back_button.configure(command=self.back_clicked)
        self.download_button.configure(command=self.download_clicked)
        self.download_button.configure(command=self.download)
        self.date_entry_default = format(date.today(), '%Y%m%d')
        self.date_entry.insert(0, self.date_entry_default)
        self.date_entry.bind('<FocusIn>', lambda x: self.date_entry.delete(0, END))

        self.load()

    def check_input(self, limit, date, type, content):
        try:
            if limit:
                limit = int(limit)
            else:
                limit = None
        except ValueError:
            raise ValueError('Limit must be an integer or empty')

        matcher = re.compile(r'^\d{8}$')
        if not matcher.match(date):
            raise ValueError('Date must be a sequence of 8 digits')

        if type == 'monthly':
            type = params.RankType.MONTHLY
        elif type == 'weekly':
            type = params.RankType.WEEKLY
        elif type == 'rookie':
            type = params.RankType.ROOKIE
        else:  # daily
            type = params.RankType.DAILY

        if content == 'manga':
            content = params.Content.MANGA
        else:  # illustration
            content = params.Content.ILLUST

        return {
            'limit': limit,
            'date': date,
            'content': content,
            'rank_type': type
        }

    def download(self):
        limit_input = self.limit_entry.get()
        date_input = self.date_entry.get()
        type_input = self.type_dropdown.get()
        content_input = self.content_dropdown.get()
        folder = self.download_folder_entry.get()
        try:
            if folder:
                folder = str(folder)
                if folder != clean_filename(folder):
                    raise ValueError('Folder name contains invalid characters')
            else:
                folder = None

            rank_params = self.check_input(limit=limit_input, date=date_input, type=type_input, content=content_input)
            rank_params['folder'] = folder
            Thread(target=self.pikax_handler.rank, kwargs=rank_params).start()
        except ValueError as e:
            import sys
            sys.stdout.write(f'Please check your inputs,\nError message:{e}')

    def back_clicked(self):
        from menu import MenuScreen
        go_to_next_screen(self, MenuScreen)

    def download_clicked(self):
        ...

    def load(self):
        for index, item in enumerate(self.labels):
            item.grid_configure(row=index)
            grid(item)

        for index, item in enumerate(self.inputs):
            item.grid_configure(row=index, column=1)
            grid(item)

        self.back_button.grid_configure(row=len(self.labels))
        self.download_button.grid_configure(row=len(self.labels), column=1)
        grid(self.back_button)
        grid(self.download_button)
        self.back_button.configure(state=NORMAL)
        self.download_button.configure(state=NORMAL)

        self.text_output.grid_configure(row=len(self.labels) + 1, columnspan=2)
        grid(self.text_output)

        self.frame.pack_configure(expand=True)
        pack(self.frame)

    def destroy(self):
        self.frame.destroy()
