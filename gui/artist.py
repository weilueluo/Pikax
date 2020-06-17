import re
import sys

import texts
from common import go_to_next_screen, download, clear_widget
from pikax import params
from models import PikaxGuiComponent

# for remembering previous inputs
_prev_id_or_url = None
_prev_content_switchbutton = None
_prev_limit = None
_prev_download_folder = None
_prev_lang = None
_prev_likes = None
_prev_pages_limit = None


class ArtistScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        # settings
        self.grid_width = 20
        self.grid_height = 18
        self.id_or_url_entry_width = 50

        # id or url input
        self.id_or_url_text_id = self.add_text(text=texts.get('ARTIST_ID_OR_URL'), row=3, column=9, columnspan=2)
        self.id_or_url_input = self.make_entry()
        self.id_or_url_input_id = self.add_widget(widget=self.id_or_url_input, row=4, column=9, columnspan=2)

        # content
        self.content_text_id = self.add_text(text=texts.get('ARTIST_CONTENT_TEXT'), row=6, column=7)
        self.content_switch_values = texts.get('ARTIST_CONTENT_SWITCH_VALUES')
        self.content_switchbutton = self.make_switchbutton(values=self.content_switch_values)
        self.content_switchbutton_id = self.add_widget(widget=self.content_switchbutton, row=6, column=12)

        # likes more than
        self.likes_text_id = self.add_text(text=texts.get('ARTIST_LIKES_TEXT'), row=8, column=7)
        self.likes_entry = self.make_entry()
        self.likes_entry_id = self.add_widget(widget=self.likes_entry, row=8, column=12)

        # limit
        self.limit_text_entry = self.make_limit_text_entry()
        self.limit_text_entry_id = self.add_widget(widget=self.limit_text_entry, row=10, column=7)
        self.limit_entry = self.make_entry()
        self.limit_entry_id = self.add_widget(widget=self.limit_entry, row=10, column=12)

        # download folder
        self.download_folder_text_id = self.add_text(text=texts.get('ARTIST_DOWNLOAD_FOLDER'), row=12, column=7)
        self.download_folder_entry = self.make_entry()
        self.download_folder_entry_id = self.add_widget(widget=self.download_folder_entry, row=12, column=12)

        # back
        self.back_button = self.make_button(text=texts.get('ARTIST_BACK'))
        self.back_button_id = self.add_widget(widget=self.back_button, row=14, column=7)

        # download button
        self.download_button = self.make_button(text=texts.get('ARTIST_DOWNLOAD'))
        self.download_button_id = self.add_widget(widget=self.download_button, row=14, column=12)

        # output
        self.output_area_id = self.add_text(text='', font=self.output_font, row=16, column=9, columnspan=2)
        self.redirect_output_to(self.output_area_id, text_widget=False)

        # config & pack
        self.inputs = [self.id_or_url_input, self.limit_entry, self.download_folder_entry, self.content_switchbutton]
        self.config()
        self.restore_prev()
        self.grid(self.frame)

    def restore_prev(self):
        global _prev_id_or_url
        global _prev_content_switchbutton
        global _prev_limit
        global _prev_download_folder
        global _prev_lang
        global _prev_likes
        global _prev_pages_limit
        if _prev_pages_limit:
            self.limit_text_entry.set(texts.values_translate(key='LIMIT_CHOICES', value=_prev_pages_limit,
                                                             src_lang=_prev_lang, dest_lang=texts.LANG))
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
        if _prev_likes:
            clear_widget(self.likes_entry)
            self.likes_entry.insert(0, str(_prev_likes))

    def config(self):
        self.id_or_url_input.configure(width=self.id_or_url_entry_width)
        self.back_button.configure(command=self.back_clicked)
        self.download_button.configure(command=self.download_clicked)
        for input_widget in self.inputs:
            input_widget.bind('<Return>', self.download_clicked)

    def _get_params(self):
        artist_id_search = re.findall(r'\d+', str(self.id_or_url_input.get()), re.S)
        limit = self.limit_entry.get().strip()
        likes_more_than = self.likes_entry.get().strip()
        if not limit:
            limit = None
        else:
            limit = int(limit)

        if not likes_more_than:
            likes_more_than = None
        else:
            likes_more_than = int(likes_more_than)

        folder = self.download_folder_entry.get()

        if len(artist_id_search) < 1:
            raise ValueError(texts.get('ARTIST_NO_ID_FOUND'))
        elif len(artist_id_search) > 1:
            raise ValueError(texts.get('ARTIST_AMBIGUOUS_ID_FOUND'))
        else:
            # ['Illustrations', 'Mangas', 'Bookmarks']
            content_input = self.content_switchbutton.get()
            if content_input == self.content_switch_values[0]:
                content = params.Content.ILLUST
            elif content_input == self.content_switch_values[1]:
                content = params.Content.MANGA
            else:
                content = params.BookmarkType.ILLUST_OR_MANGA

            artist_id = artist_id_search[0]
            return {
                'artist_id': artist_id,
                'folder': str(folder),
                'limit': limit,
                'content': content,
                'likes': likes_more_than,
                # ['pages limit', 'artworks limit']
                'pages_limit': texts.get('LIMIT_CHOICES')[0] == self.limit_text_entry.get()
            }

    def download_clicked(self, _=None):
        try:
            kwargs = self._get_params()
            download(target=self.pikax_handler.download_by_artist_id, kwargs=kwargs)
        except ValueError as e:
            sys.stdout.write(str(e))

    def save_inputs(self):
        global _prev_id_or_url
        global _prev_content_switchbutton
        global _prev_limit
        global _prev_download_folder
        global _prev_lang
        global _prev_likes
        global _prev_pages_limit
        _prev_pages_limit = self.limit_text_entry.get()
        _prev_lang = texts.LANG
        _prev_id_or_url = self.id_or_url_input.get()
        _prev_content_switchbutton = self.content_switchbutton.get()
        _prev_limit = self.limit_entry.get()
        _prev_download_folder = self.download_folder_entry.get()
        _prev_likes = self.likes_entry.get()

    def back_clicked(self):
        from menu import MenuScreen
        self.save_inputs()
        go_to_next_screen(src=self, dest=MenuScreen)
