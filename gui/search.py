import sys

import texts
from common import go_to_next_screen, download, clear_widget
from pikax.util import clean_filename
from models import PikaxGuiComponent

# for remembering previous
_prev_keyword_text = None
_prev_limit_text = None
_prev_match_text = None
_prev_sort_text = None
_prev_popularity_text = None
_prev_download_folder_text = None
_prev_lang = None
_prev_pages_limit = None


class SearchScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        self.grid_height = 10
        self.grid_width = 15

        # labels
        self.keyword_text_id = self.add_text(text=texts.get('SEARCH_KEYWORD'), column=5, row=1)
        self.limit_text_entry = self.make_limit_text_entry()
        self.limit_text_entry_id = self.add_widget(widget=self.limit_text_entry, column=5, row=2)
        self.match_text_id = self.add_text(text=texts.get('SEARCH_MATCH'), column=5, row=3)
        self.sort_text_id = self.add_text(text=texts.get('SEARCH_SORT'), column=5, row=4)
        self.popularity_text_id = self.add_text(text=texts.get('SEARCH_POPULARITY'), column=5, row=5)
        self.download_folder_text_id = self.add_text(text=texts.get('SEARCH_DOWNLOAD_FOLDER'), column=5, row=6)

        # create inputs
        self.keyword_entry = self.make_entry()
        self.limit_entry = self.make_entry()
        self.match_choices = texts.get('SEARCH_MATCH_CHOICES')  # ['exact', 'partial', 'any']
        self.match_dropdown = self.make_dropdown(self.match_choices[1], self.match_choices)
        self.sort_choices = texts.get('SEARCH_SORT_CHOICES')  # ['date ascending', 'date descending']
        self.sort_dropdown = self.make_dropdown(self.sort_choices[1], self.sort_choices)
        # ['any', '100', '500', '1000', '5000', '10000', '20000']
        self.popularity_choices = texts.get('SEARCH_POPULARITY_CHOICES')
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
        self.search_and_download_button = self.make_button(text=texts.get('SEARCH_DOWNLOAD'))
        self.back_button = self.make_button(text=texts.get('SEARCH_BACK'))

        # add buttons
        self.back_button_id = self.add_widget(widget=self.back_button, column=5, row=7)
        self.search_and_download_button_id = self.add_widget(self.search_and_download_button, column=9, row=7)

        # add output
        self.output_id = self.add_text(text='', row=8, column=7, font=self.output_font)
        self.redirect_output_to(self.output_id, text_widget=False)

        # config
        self.config()
        self.restore_prev()

    def restore_prev(self):
        global _prev_keyword_text
        global _prev_limit_text
        global _prev_match_text
        global _prev_sort_text
        global _prev_popularity_text
        global _prev_download_folder_text
        global _prev_pages_limit
        if _prev_keyword_text:
            clear_widget(self.keyword_entry)
            self.keyword_entry.insert(0, _prev_keyword_text)
        if _prev_limit_text:
            clear_widget(self.limit_entry)
            self.limit_entry.insert(0, _prev_limit_text)
        if _prev_match_text:
            clear_widget(self.match_dropdown)
            self.match_dropdown.set(texts.values_translate(key='SEARCH_MATCH_CHOICES',
                                                           value=_prev_match_text,
                                                           src_lang=_prev_lang,
                                                           dest_lang=texts.LANG
                                                           ))
        if _prev_sort_text:
            clear_widget(self.sort_dropdown)
            self.sort_dropdown.set(texts.values_translate(key='SEARCH_SORT_CHOICES',
                                                          value=_prev_sort_text,
                                                          src_lang=_prev_lang,
                                                          dest_lang=texts.LANG
                                                          ))
        if _prev_popularity_text:
            clear_widget(self.popularity_dropdown)
            self.popularity_dropdown.set(texts.values_translate(key='SEARCH_POPULARITY_CHOICES',
                                                                value=_prev_popularity_text,
                                                                src_lang=_prev_lang,
                                                                dest_lang=texts.LANG
                                                                ))
        if _prev_download_folder_text:
            clear_widget(self.download_folder_entry)
            self.download_folder_entry.insert(0, _prev_download_folder_text)

        if _prev_pages_limit:
            self.limit_text_entry.set(texts.values_translate(key='LIMIT_CHOICES', value=_prev_pages_limit,
                                                             src_lang=_prev_lang, dest_lang=texts.LANG))

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
        self.grid(self.frame)
        inputs[0].focus_set()

    def config_buttons(self):
        self.search_and_download_button.configure(command=self.search_and_download_clicked)
        self.back_button.configure(command=self.back_clicked)

    def destroy(self):
        self.frame.destroy()

    def save_inputs(self):
        global _prev_keyword_text
        global _prev_limit_text
        global _prev_match_text
        global _prev_sort_text
        global _prev_popularity_text
        global _prev_download_folder_text
        global _prev_lang
        global _prev_pages_limit
        _prev_pages_limit = self.limit_text_entry.get()
        _prev_lang = texts.LANG
        _prev_keyword_text = self.keyword_entry.get()
        _prev_limit_text = self.limit_entry.get()
        _prev_match_text = self.match_dropdown.get()
        _prev_sort_text = self.sort_dropdown.get()
        _prev_popularity_text = self.popularity_dropdown.get()
        _prev_download_folder_text = self.download_folder_entry.get()

    def back_clicked(self):
        from menu import MenuScreen
        self.save_inputs()
        go_to_next_screen(src=self, dest=MenuScreen)

    def search_and_download_clicked(self, _=None):
        try:
            keyword = str(self.keyword_entry.get())
            if not keyword:
                raise ValueError(texts.get('SEARCH_EMPTY_KEYWORD_ERROR'))

            folder_input = str(self.download_folder_entry.get())
            if folder_input != clean_filename(folder_input):
                raise ValueError(texts.get('SEARCH_INVALID_FOLDER_ERROR'))
            folder = folder_input or None

            try:
                limit_input = int(self.limit_entry.get()) if self.limit_entry.get() else None
            except ValueError:
                raise ValueError(texts.get('SEARCH_LIMIT_ERROR'))
            match_input = str(self.match_dropdown.get())
            sort_input = str(self.sort_dropdown.get())
            popularity_input = str(self.popularity_dropdown.get())
            limit_type_input = str(self.limit_text_entry.get())
            params = self.check_inputs(limit_input=limit_input, match_input=match_input, sort_input=sort_input,
                                       popularity_input=popularity_input, limit_type_input=limit_type_input)
        except (TypeError, ValueError) as e:
            sys.stdout.write(texts.get('SEARCH_ERROR_MESSAGE').format(error_message=str(e)))
            return

        params['keyword'] = keyword
        params['folder'] = folder
        download(target=self.pikax_handler.search, kwargs=params)

    def check_inputs(self, limit_input, match_input, sort_input, popularity_input, limit_type_input):
        from pikax import params
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
            'popularity': popularity,
            # ['pages limit', 'artworks limit']
            'pages_limit': limit_type_input == texts.get('LIMIT_CHOICES')[0]
        }


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()
    SearchScreen(root, None)
    root.mainloop()
