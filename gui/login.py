import webbrowser
from threading import Thread
from tkinter import *
from tkinter import font

import settings
from common import go_to_next_screen, get_background_file_path
from lib.pikax.exceptions import PikaxException
from menu import MenuScreen
from models import PikaxGuiComponent


class LoginScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        # settings
        # sizes
        self.grid_height = 30
        self.grid_width = 11

        # text
        self.username_text = 'username'
        self.password_text = 'password'
        self.login_button_text = 'Login'
        self.guest_button_text = 'Guest'
        self.register_text = 'Register'

        # make entries & button
        self.username_entry = self.make_entry()
        self.password_entry = self.make_entry()
        self.login_button = self.make_button(text=self.login_button_text)
        self.guest_button = self.make_button(text=self.guest_button_text)
        self.register_button = self.make_button(text=self.register_text)

        # add text
        self.canvas_username = self.add_text(text=self.username_text, row=9, column=4, columnspan=3)
        self.canvas_password = self.add_text(text=self.password_text, row=14, column=4, columnspan=3)

        # add entries & button to canvas
        self.username_entry_id = self.add_widget(widget=self.username_entry, row=11, column=4, columnspan=3)
        self.password_entry_id = self.add_widget(widget=self.password_entry, row=16, column=4, columnspan=3)
        self.guest_button_id = self.add_widget(widget=self.guest_button, row=20, column=3)
        self.login_button_id = self.add_widget(widget=self.login_button, row=20, column=5)
        self.register_button_id = self.add_widget(widget=self.register_button, row=20, column=7)
        self.output_id = self.add_text(text='', row=24, column=4, columnspan=3, font=self.output_font)

        self.config_texts([self.canvas_username, self.canvas_password, self.output_id])
        self.config_buttons()
        self.config_output()
        self.config_entries()

        self.pack(self.frame, expand=True)
        self.username_entry.focus_set()

    def make_entry(self):
        entry = super().make_entry()
        entry.configure(width=27)
        return entry

    def config_texts(self, texts):
        for item in texts:
            self.canvas.itemconfigure(item, fill=self.display_text_color)

    def config_output(self):
        self.redirect_output_to(self.output_id, text_widget=False)

    def config_buttons(self):
        self.login_button.configure(command=self.login)
        self.guest_button.configure(command=self.guest_login)
        self.register_button.configure(command=self.register_button_pressed)

    def config_entries(self):
        self.username_entry.bind('<Return>', self.login)
        self.password_entry.bind('<Return>', self.login)
        self.password_entry.configure(show="\u2022")  # bullet

    @staticmethod
    def register_button_pressed():
        webbrowser.open(settings.PIXIV_REGISTER_URL)

    def login(self, _=None):
        Thread(target=self._login).start()

    def _login(self):
        self.login_button.configure(state=DISABLED)
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            self.pikax_handler.login(username, password)
            go_to_next_screen(src=self, dest=MenuScreen)
        except PikaxException as e:
            self.login_button.configure(state=NORMAL)
            sys.stdout.write(f'{e}')

    def guest_login(self):
        go_to_next_screen(src=self, dest=MenuScreen)

    def destroy(self):
        self.frame.destroy()
