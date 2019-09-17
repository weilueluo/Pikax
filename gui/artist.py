import re
import sys

import texts
from common import go_to_next_screen, download, clear_widget
from lib.pikax import params
from models import PikaxGuiComponent

# for remembering previous inputs
_prev_id_or_url = None
_prev_content_switchbutton = None
_prev_limit = None
_prev_download_folder = None
_prev_lang = None


class ArtistScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        # settings
        self.grid_width = 20
        self.grid_height = 18
        self.id_or_url_entry_width = 50

        # id or url input
        self.id_or_url_text_id = self.add_text(text=texts.get('ARTIST_ID_OR_URL'), row=4, column=9, columnspan=2)
        self.id_or_url_input = self.make_entry()
        self.id_or_url_input_id = self.add_widget(widget=self.id_or_url_input, row=5, column=9, columnspan=2)

        # content
        self.content_text_id = self.add_text(text=texts.get('ARTIST_CONTENT_TEXT'), row=7, column=7)
        self.content_switch_values = texts.get('ARTIST_CONTENT_SWITCH_VALUES')
        self.content_switchbutton = self.make_switchbutton(values=self.content_switch_values)
        self.content_switchbutton_id = self.add_widget(widget=self.content_switchbutton, row=7, column=12)

        # limit
        self.limit_text_id = self.add_text(text=texts.get('ARTIST_LIMIT_TEXT'), row=9, column=7)
        self.limit_entry = self.make_entry()
        self.limit_entry_id = self.add_widget(widget=self.limit_entry, row=9, column=12)

        # download folder
        self.download_folder_text_id = self.add_text(text=texts.get('ARTIST_DOWNLOAD_FOLDER'), row=11, column=7)
        self.download_folder_entry = self.make_entry()
        self.download_folder_entry_id = self.add_widget(widget=self.download_folder_entry, row=11, column=12)

        # back
        self.back_button = self.make_button(text=texts.get('ARTIST_BACK'))
        self.back_button_id = self.add_widget(widget=self.back_button, row=13, column=7)

        # download button
        self.download_button = self.make_button(text=texts.get('ARTIST_DOWNLOAD'))
        self.download_button_id = self.add_widget(widget=self.download_button, row=13, column=12)

        # output
        self.output_area_id = self.add_text(text='', font=self.output_font, row=15, column=9, columnspan=2)
        self.redirect_output_to(self.output_area_id, text_widget=False)

        # config & pack
        self.inputs = [self.id_or_url_input, self.limit_entry, self.download_folder_entry, self.content_switchbutton]
        self.config()
        self.restore_prev()
        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

    def restore_prev(self):
        global _prev_id_or_url
        global _prev_content_switchbutton
        global _prev_limit
        global _prev_download_folder
        global _prev_lang
        if _prev_id_or_url:
            clear_widget(self.id_or_url_input)
            self.id_or_url_input.insert(0, str(_prev_id_or_url))
        if _prev_content_switchbutton:
            self.content_switchbutton.set(texts.values_translate(key='ARTIST_CONTENT_SWITCH_VALUES',
                                                                 value=_prev_content_switchbutton,
                                                                 src_lang=_prev_lang,
                                                                 dest_lang=texts.LANG
                                                                 ))
        if _prev_limit:
            clear_widget(self.limit_entry)
            self.limit_entry.insert(0, str(_prev_limit))
        if _prev_download_folder:
            clear_widget(self.download_folder_entry)
            self.download_folder_entry.insert(0, str(_prev_download_folder))

    def config(self):
        self.id_or_url_input.configure(width=self.id_or_url_entry_width)
        self.back_button.configure(command=self.back_clicked)
        self.download_button.configure(command=self.download_clicked)
        for input_widget in self.inputs:
            input_widget.bind('<Return>', self.download_clicked)

    def download_clicked(self, _=None):
        artist_id_search = re.findall(r'\d+', str(self.id_or_url_input.get()), re.S)
        limit = self.limit_entry.get().strip()
        if not limit:
            limit = None
        else:
            limit = int(limit)
        folder = self.download_folder_entry.get()

        if len(artist_id_search) < 1:
            sys.stdout.write(texts.get('ARTIST_NO_ID_FOUND'))
        elif len(artist_id_search) > 1:
            sys.stdout.write(texts.get('ARTIST_AMBIGUOUS_ID_FOUND'))
        else:
            # ['Illustrations', 'Mangas', 'Bookmarks']
            content_input = self.content_switchbutton.get()
            if content_input == self.content_switch_values[0]:
                content = params.ContentType.ILLUST
            elif content_input == self.content_switch_values[1]:
                content = params.ContentType.MANGA
            else:
                content = params.ContentType.BOOKMARK

            artist_id = artist_id_search[0]
            param = {
                'artist_id': artist_id,
                'folder': str(folder),
                'limit': limit,
                'content': content
            }
            download(target=self.pikax_handler.download_by_artist_id, kwargs=param)

    def save_inputs(self):
        global _prev_id_or_url
        global _prev_content_switchbutton
        global _prev_limit
        global _prev_download_folder
        global _prev_lang
        _prev_lang = texts.LANG
        _prev_id_or_url = self.id_or_url_input.get()
        _prev_content_switchbutton = self.content_switchbutton.get()
        _prev_limit = self.limit_entry.get()
        _prev_download_folder = self.download_folder_entry.get()

    def back_clicked(self):
        from menu import MenuScreen
        self.save_inputs()
        go_to_next_screen(src=self, dest=MenuScreen)
