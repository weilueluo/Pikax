import os
import sys
import tkinter as tk
import webbrowser
from threading import Thread

import settings
import texts
from account import Account
from common import go_to_next_screen, load_from_local, save_to_local, remove_local_file, clear_widgets
from pikax import PikaxException
from menu import MenuScreen
from models import PikaxGuiComponent

_prev_username = ''
_prev_password = ''
_prev_checkbox = None


class LoginScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        # settings
        # sizes
        self.grid_height = 30
        self.grid_width = 11

        # text
        self.username_text = texts.get('LOGIN_USERNAME')
        self.password_text = texts.get('LOGIN_PASSWORD')
        self.login_button_text = texts.get('LOGIN_LOGIN_BUTTON')
        self.guest_button_text = texts.get('LOGIN_GUEST_BUTTON')
        self.register_text = texts.get('LOGIN_REGISTER_BUTTON')

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
        self.output_id = self.add_text(text='', row=26, column=4, columnspan=3, font=self.output_font)

        # add checkbox
        self.remember_me_checkbox = self.make_checkbutton(text=texts.get('LOGIN_REMEMBER_TEXT'))
        self.remember_me_checkbox_id = self.add_widget(widget=self.remember_me_checkbox, row=24, column=5)

        self.config_buttons()
        self.config_output()
        self.config_entries()

        self.grid(self.frame)
        self.username_entry.focus_set()

        #
        # default operations
        #

        self.restore_previous()

    def restore_previous(self):
        global _prev_username
        global _prev_password
        global _prev_checkbox
        self.clear_username_and_password()
        self.fill_username_and_password(username=_prev_username, password=_prev_password)
        if not (_prev_checkbox is None):
            self.remember_me_checkbox.set(_prev_checkbox)
        elif os.path.isfile(settings.LOGIN_CREDENTIAL_FILE):
            self.remember_me_checkbox.set(True)

    def clear_username_and_password(self):
        clear_widgets([self.username_entry, self.password_entry])

    def fill_username_and_password(self, username='', password=''):
        self.username_entry.insert(0, username)
        self.password_entry.insert(0, password)

    def login_if_credential_exists(self):
        credential_file = settings.LOGIN_CREDENTIAL_FILE
        if os.path.isfile(credential_file):
            account = load_from_local(credential_file)

            if not account:  # corrupted
                return

            self.clear_username_and_password()
            try:
                self.fill_username_and_password(username=str(account.username), password=str(account.password))
                self.login()
            except AttributeError:
                # using old credential file, self.username has changed to be a property
                # and internal renamed to self._username
                remove_local_file(credential_file)

    def make_entry(self, **kwargs):
        entry = super().make_entry(**kwargs)
        entry.configure(width=27)
        return entry

    def config_output(self):
        self.redirect_output_to(self.output_id, text_widget=False)

    def config_buttons(self):
        self.login_button.configure(command=self.login)
        self.guest_button.configure(command=self.guest_login)
        self.register_button.configure(command=self.register_button_pressed)

    def config_entries(self):
        self.username_entry.bind('<Return>', self.login)
        self.password_entry.bind('<Return>', self.login)
        self.password_entry.configure(show=texts.get('BULLET'))

    @staticmethod
    def register_button_pressed():
        webbrowser.open(settings.PIXIV_REGISTER_URL)

    def login(self, _=None):
        self.save_inputs()
        Thread(target=self._login).start()

    def save_inputs(self):
        global _prev_password
        global _prev_username
        global _prev_checkbox
        _prev_checkbox = self.remember_me_checkbox.get()
        _prev_username = self.username_entry.get()
        _prev_password = self.password_entry.get()

    def _login(self):
        self.login_button.configure(state=tk.DISABLED)
        self.guest_button.configure(state=tk.DISABLED)
        self.language_button.configure(state=tk.DISABLED)
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            self.pikax_handler.login(username, password)
            if self.remember_me_checkbox.get():
                self.save_login_credential(username, password)
            else:
                self.remove_login_credential_if_exists()
            go_to_next_screen(src=self, dest=MenuScreen)
        except PikaxException as e:
            self.guest_button.configure(state=tk.NORMAL)
            self.language_button.configure(state=tk.NORMAL)
            self.login_button.configure(state=tk.NORMAL)
            sys.stdout.write(f'{e}')

    def remove_login_credential_if_exists(self):
        credential_file = settings.LOGIN_CREDENTIAL_FILE
        if os.path.isfile(credential_file):
            remove_local_file(credential_file)

    def save_login_credential(self, username, password):
        credential_file = settings.LOGIN_CREDENTIAL_FILE
        account = Account(username=username, password=password)
        save_to_local(file_path=credential_file, item=account)

    def guest_login(self):
        self.save_inputs()
        self.login_button.configure(state=tk.DISABLED)
        self.language_button.configure(state=tk.DISABLED)
        go_to_next_screen(src=self, dest=MenuScreen)

    def destroy(self):
        self.frame.destroy()
