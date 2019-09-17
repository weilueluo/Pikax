import re
from datetime import date

import texts
from common import go_to_next_screen, download, clear_widget
from lib.pikax import params
from lib.pikax.util import clean_filename
from models import PikaxGuiComponent

# for remembering previous inputs
_prev_date_entry = None
_prev_limit_entry = None
_prev_type_dropdown = None
_prev_content_dropdown = None
_prev_download_folder_entry = None
_prev_lang = None


class RankScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        self.grid_width = 15
        self.grid_height = 10

        # texts
        self.date_text_id = self.add_text(text=texts.get('RANK_DATE'), row=2, column=5)
        self.limit_text_id = self.add_text(text=texts.get('RANK_LIMIT'), row=3, column=5)
        self.type_text_id = self.add_text(text=texts.get('RANK_TYPE'), row=4, column=5)
        self.content_text_id = self.add_text(text=texts.get('RANK_CONTENT'), row=5, column=5)
        self.download_folder_text_id = self.add_text(text=texts.get('RANK_DOWNLOAD_FOLDER'), row=6, column=5)

        # create inputs
        self.date_entry = self.make_entry()
        self.date_entry.insert(0, format(date.today(), '%Y%m%d'))
        self.limit_entry = self.make_entry()
        self.rank_types = texts.get('RANK_TYPES')
        self.type_dropdown = self.make_dropdown(self.rank_types[0], self.rank_types)
        self.content_types = texts.get('RANK_CONTENT_TYPES')
        self.content_dropdown = self.make_dropdown(self.content_types[0], self.content_types)
        self.download_folder_entry = self.make_entry()

        # add inputs
        self.date_entry_id = self.add_widget(widget=self.date_entry, row=2, column=9)
        self.limit_entry_id = self.add_widget(widget=self.limit_entry, row=3, column=9)
        self.type_dropdown_id = self.add_widget(widget=self.type_dropdown, row=4, column=9)
        self.content_dropdown_id = self.add_widget(widget=self.content_dropdown, row=5, column=9)
        self.download_folder_entry_id = self.add_widget(widget=self.download_folder_entry, row=6, column=9)

        # create buttons
        self.back_button = self.make_button(text=texts.get('RANK_BACK'))
        self.download_button = self.make_button(text=texts.get('RANK_DOWNLOAD'))

        # add buttons
        self.back_button_id = self.add_widget(widget=self.back_button, row=7, column=5)
        self.download_button_id = self.add_widget(self.download_button, row=7, column=9)

        # output
        self.output_id = self.add_text(text='', row=8, column=5, columnspan=4, font=self.output_font)
        self.redirect_output_to(self.output_id, text_widget=False)

        # config
        self.config()
        self.restore_prev()
        self.pack(self.frame, expand=True)

    def restore_prev(self):
        global _prev_date_entry
        global _prev_limit_entry
        global _prev_type_dropdown
        global _prev_content_dropdown
        global _prev_download_folder_entry
        if _prev_date_entry:
            clear_widget(self.date_entry)
            self.date_entry.insert(0, _prev_date_entry)
        if _prev_limit_entry:
            clear_widget(self.limit_entry)
            self.limit_entry.insert(0, _prev_limit_entry)
        if _prev_type_dropdown:
            self.type_dropdown.set(texts.values_translate(key='RANK_TYPES', value=_prev_type_dropdown,
                                                          src_lang=_prev_lang, dest_lang=texts.LANG))
        if _prev_content_dropdown:
            self.content_dropdown.set(texts.values_translate(key='RANK_CONTENT_TYPES', value=_prev_content_dropdown,
                                                             src_lang=_prev_lang, dest_lang=texts.LANG))
        if _prev_download_folder_entry:
            clear_widget(self.download_folder_entry)
            self.download_folder_entry.insert(0, _prev_download_folder_entry)

    def config(self):
        inputs = [
            self.date_entry,
            self.limit_entry,
            self.type_dropdown,
            self.content_dropdown,
            self.download_folder_entry
        ]
        self.config_buttons()
        for input_widget in inputs:
            input_widget.bind('<Return>', self.download_clicked)
        inputs[0].focus_set()

    def config_buttons(self):
        self.back_button.configure(command=self.back_clicked)
        self.download_button.configure(command=self.download_clicked)

    def check_input(self, limit, date, rank_type, content):
        try:
            if limit:
                limit = int(limit)
            else:
                limit = None
        except ValueError:
            raise ValueError(texts.get('RANK_LIMIT_ERROR'))

        matcher = re.compile(r'^\d{8}$')
        if not matcher.match(date):
            raise ValueError(texts.get('RANK_DATE_ERROR'))

        #  ['daily', 'weekly', 'monthly', 'rookie']
        if rank_type == self.rank_types[2]:
            rank_type = params.RankType.MONTHLY
        elif rank_type == self.rank_types[1]:
            rank_type = params.RankType.WEEKLY
        elif rank_type == self.rank_types[3]:
            rank_type = params.RankType.ROOKIE
        else:  # daily
            rank_type = params.RankType.DAILY

        # ['illustration', 'manga']
        if content == self.content_types[1]:
            content = params.Content.MANGA
        else:  # illustration
            content = params.Content.ILLUST

        return {
            'limit': limit,
            'date': date,
            'content': content,
            'rank_type': rank_type
        }

    def download_clicked(self, _=None):
        limit_input = self.limit_entry.get()
        date_input = self.date_entry.get()
        type_input = self.type_dropdown.get()
        content_input = self.content_dropdown.get()
        folder = self.download_folder_entry.get()
        try:
            if folder:
                folder = str(folder)
                if folder != clean_filename(folder):
                    raise ValueError(texts.get('RANK_INVALID_FOLDER_ERROR'))
            else:
                folder = None

            rank_params = self.check_input(limit=limit_input, date=date_input, rank_type=type_input,
                                           content=content_input)
            rank_params['folder'] = folder
            download(target=self.pikax_handler.rank, kwargs=rank_params)

        except ValueError as e:
            import sys
            sys.stdout.write(texts.get('RANK_ERROR_MESSAGE').format(error_message=str(e)))

    def save_inputs(self):
        global _prev_date_entry
        global _prev_limit_entry
        global _prev_type_dropdown
        global _prev_content_dropdown
        global _prev_download_folder_entry
        global _prev_lang
        _prev_date_entry = self.date_entry.get()
        _prev_limit_entry = self.limit_entry.get()
        _prev_type_dropdown = self.type_dropdown.get()
        _prev_content_dropdown = self.content_dropdown.get()
        _prev_download_folder_entry = self.download_folder_entry.get()
        _prev_lang = texts.LANG

    def back_clicked(self):
        from menu import MenuScreen
        self.save_inputs()
        go_to_next_screen(self, MenuScreen)

    def destroy(self):
        self.frame.destroy()
