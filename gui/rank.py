import re
from datetime import date

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
        self.date_text_id = self.add_text(text='date', row=2, column=5)
        self.limit_text_id = self.add_text(text='limit', row=3, column=5)
        self.type_text_id = self.add_text(text='type', row=4, column=5)
        self.content_text_id = self.add_text(text='content', row=5, column=5)
        self.download_folder_text_id = self.add_text(text='download folder', row=6, column=5)

        # create inputs
        self.date_entry = self.make_entry()
        self.date_entry.insert(0, format(date.today(), '%Y%m%d'))
        self.limit_entry = self.make_entry()
        rank_types = ['daily', 'weekly', 'monthly', 'rookie']
        self.type_dropdown = self.make_dropdown('daily', rank_types)
        content_types = ['illustration', 'manga']
        self.content_dropdown = self.make_dropdown('illustration', content_types)
        self.download_folder_entry = self.make_entry()

        # add inputs
        self.date_entry_id = self.add_widget(widget=self.date_entry, row=2, column=9)
        self.limit_entry_id = self.add_widget(widget=self.limit_entry, row=3, column=9)
        self.type_dropdown_id = self.add_widget(widget=self.type_dropdown, row=4, column=9)
        self.content_dropdown_id = self.add_widget(widget=self.content_dropdown, row=5, column=9)
        self.download_folder_entry_id = self.add_widget(widget=self.download_folder_entry, row=6, column=9)

        # create buttons
        self.back_button = self.make_button(text='back')
        self.download_button = self.make_button(text='download')

        # add buttons
        self.back_button_id = self.add_widget(widget=self.back_button, row=7, column=5)
        self.download_button_id = self.add_widget(self.download_button, row=7, column=9)

        # output
        self.output_id = self.add_text(text='', row=8, column=5, columnspan=4)
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
                    raise ValueError('Folder name contains invalid characters')
            else:
                folder = None

            rank_params = self.check_input(limit=limit_input, date=date_input, type=type_input, content=content_input)
            rank_params['folder'] = folder
            download(target=self.pikax_handler.rank, kwargs=rank_params)

        except ValueError as e:
            import sys
            sys.stdout.write(f'Please check your inputs,\nError message:{e}')

    def back_clicked(self):
        from menu import MenuScreen
        go_to_next_screen(self, MenuScreen)

    def destroy(self):
        self.frame.destroy()
