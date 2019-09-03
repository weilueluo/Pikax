import re
from datetime import date

import texts
from common import go_to_next_screen, download
from lib.pikax import params
from lib.pikax.util import clean_filename
from models import PikaxGuiComponent


class RankScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        self.grid_width = 15
        self.grid_height = 10

        # texts
        self.date_text_id = self.add_text(text=texts.RANK_DATE, row=2, column=5)
        self.limit_text_id = self.add_text(text=texts.RANK_LIMIT, row=3, column=5)
        self.type_text_id = self.add_text(text=texts.RANK_TYPE, row=4, column=5)
        self.content_text_id = self.add_text(text=texts.RANK_CONTENT, row=5, column=5)
        self.download_folder_text_id = self.add_text(text=texts.RANK_DOWNLOAD_FOLDER, row=6, column=5)

        # create inputs
        self.date_entry = self.make_entry()
        self.date_entry.insert(0, format(date.today(), '%Y%m%d'))
        self.limit_entry = self.make_entry()
        self.rank_types = texts.RANK_TYPES
        self.type_dropdown = self.make_dropdown(self.rank_types[0], self.rank_types)
        self.content_types = texts.RANK_CONTENT_TYPES
        self.content_dropdown = self.make_dropdown(self.content_types[0], self.content_types)
        self.download_folder_entry = self.make_entry()

        # add inputs
        self.date_entry_id = self.add_widget(widget=self.date_entry, row=2, column=9)
        self.limit_entry_id = self.add_widget(widget=self.limit_entry, row=3, column=9)
        self.type_dropdown_id = self.add_widget(widget=self.type_dropdown, row=4, column=9)
        self.content_dropdown_id = self.add_widget(widget=self.content_dropdown, row=5, column=9)
        self.download_folder_entry_id = self.add_widget(widget=self.download_folder_entry, row=6, column=9)

        # create buttons
        self.back_button = self.make_button(text=texts.RANK_BACK)
        self.download_button = self.make_button(text=texts.RANK_DOWNLOAD)

        # add buttons
        self.back_button_id = self.add_widget(widget=self.back_button, row=7, column=5)
        self.download_button_id = self.add_widget(self.download_button, row=7, column=9)

        # output
        self.output_id = self.add_text(text='', row=8, column=5, columnspan=4, font=self.output_font)
        self.redirect_output_to(self.output_id, text_widget=False)

        # config
        self.config_buttons()
        for widget in self.frame.children.values():
            widget.bind('<Return>', self.download_clicked)
        self.date_entry.focus_set()
        self.pack(self.frame, expand=True)

    def config_buttons(self):
        self.back_button.configure(command=self.back_clicked)
        self.download_button.configure(command=self.download_clicked)

    def check_input(self, limit, date, type, content):
        try:
            if limit:
                limit = int(limit)
            else:
                limit = None
        except ValueError:
            raise ValueError(texts.RANK_LIMIT_ERROR)

        matcher = re.compile(r'^\d{8}$')
        if not matcher.match(date):
            raise ValueError(texts.RANK_DATE_ERROR)

        #  ['daily', 'weekly', 'monthly', 'rookie']
        if type == self.rank_types[2]:
            type = params.RankType.MONTHLY
        elif type == self.rank_types[1]:
            type = params.RankType.WEEKLY
        elif type == self.rank_types[3]:
            type = params.RankType.ROOKIE
        else:  # daily
            type = params.RankType.DAILY

        # ['illustration', 'manga']
        if content == self.content_types[1]:
            content = params.Content.MANGA
        else:  # illustration
            content = params.Content.ILLUST

        return {
            'limit': limit,
            'date': date,
            'content': content,
            'rank_type': type
        }

    def download_clicked(self, event=None):
        limit_input = self.limit_entry.get()
        date_input = self.date_entry.get()
        type_input = self.type_dropdown.get()
        content_input = self.content_dropdown.get()
        folder = self.download_folder_entry.get()
        try:
            if folder:
                folder = str(folder)
                if folder != clean_filename(folder):
                    raise ValueError(texts.RANK_INVALID_FOLDER_ERROR)
            else:
                folder = None

            rank_params = self.check_input(limit=limit_input, date=date_input, type=type_input, content=content_input)
            rank_params['folder'] = folder
            download(target=self.pikax_handler.rank, kwargs=rank_params)

        except ValueError as e:
            import sys
            sys.stdout.write(texts.RANK_ERROR_MESSAGE.format(error_message=str(e)))

    def back_clicked(self):
        from menu import MenuScreen
        go_to_next_screen(self, MenuScreen)

    def destroy(self):
        self.frame.destroy()
