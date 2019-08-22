import re
import sys
from datetime import date
from threading import Thread
from tkinter import NORMAL, DISABLED, END

from common import StdoutRedirector, go_to_next_screen
from lib.pikax import params
from lib.pikax.util import clean_filename
from models import PikaxGuiComponent


class RankScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        # labels
        self.date_label = self.make_label('date')
        self.limit_label = self.make_label('limit')
        self.type_label = self.make_label('type')
        self.content_label = self.make_label('content')
        self.download_folder_label = self.make_label('download folder')

        self.labels = [
            self.date_label,
            self.limit_label,
            self.type_label,
            self.content_label,
            self.download_folder_label
        ]

        # inputs
        self.date_entry = self.make_entry()
        self.date_entry.insert(0, format(date.today(), '%Y%m%d'))
        self.limit_entry = self.make_entry()
        rank_types = ['daily', 'weekly', 'monthly', 'rookie']
        self.type_dropdown = self.make_dropdown('daily', rank_types)
        content_types = ['illustration', 'manga']
        self.content_dropdown = self.make_dropdown('illustration', content_types)
        self.download_folder_entry = self.make_entry()

        self.inputs = [
            self.date_entry,
            self.limit_entry,
            self.type_dropdown,
            self.content_dropdown,
            self.download_folder_entry
        ]

        # buttons
        self.back_button = self.make_button('back')
        self.download_button = self.make_button('rank and download')
        self.back_button.configure(command=self.back_clicked)
        self.download_button.configure(command=self.download_clicked)
        self.download_button.configure(command=self.download)

        # download outputs
        self.download_output = self.make_download_output()
        self.redirect_output_to(self.download_output)

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
        # labels
        for index, item in enumerate(self.labels):
            item.grid_configure(row=index)
            self.grid(item)
        # entries
        for index, item in enumerate(self.inputs):
            item.grid_configure(row=index, column=1)
            self.grid(item)

        # buttons
        self.back_button.grid_configure(row=len(self.labels))
        self.download_button.grid_configure(row=len(self.labels), column=1)
        self.grid(self.back_button)
        self.grid(self.download_button)
        self.back_button.configure(state=NORMAL)
        self.download_button.configure(state=NORMAL)

        # download output
        self.download_output.grid_configure(row=len(self.labels) + 1, columnspan=2)
        self.grid(self.download_output)

        # frame
        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

    def destroy(self):
        self.frame.destroy()
