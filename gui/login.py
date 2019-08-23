import sys
from threading import Thread
from tkinter import DISABLED, CENTER, NORMAL, Text

from common import go_to_next_screen
from lib.pikax.exceptions import PikaxException
from models import PikaxGuiComponent

class LoginScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.title_label = self.make_label(text='Pikax')
        self.title_label.configure(font="-weight bold", anchor=CENTER)
        self.username_label = self.make_label(text='username')
        self.password_label = self.make_label(text='password')
        self.username_entry = self.make_entry()
        self.password_entry = self.make_entry()
        self.output_text = self.make_entry()
        self.contact_label = self.make_download_output()
        self.contact_label.configure(bg='grey95', fg='grey50')
        self.contact_label.configure(state=NORMAL)
        self.contact_label.tag_configure("center", justify=CENTER)
        self.contact_label.insert(0.0, 'Issue? report @ https://github.com/Redcxx/Pikax/issues')
        self.contact_label.tag_add("center", "1.0", "end")
        self.contact_label.configure(state=DISABLED)
        self.login_button = self.make_button(text='login')

        self.login_button.configure(command=self.login)
        self.username_entry.bind('<Return>', self.login)
        self.password_entry.bind('<Return>', self.login)
        self.password_entry.configure(show="\u2022")  # bullet
        self.output_text.configure(state=DISABLED, justify=CENTER, width=60)
        self.redirect_output_to(self.output_text)

        self.components = [
            self.title_label,
            self.username_label,
            self.username_entry,
            self.password_label,
            self.password_entry,
            self.login_button,
            self.output_text,
            self.contact_label
        ]

        self.load()

    def login(self, event=None):
        Thread(target=self._login).start()

    def _login(self):
        self.login_button.configure(state=DISABLED)
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            self.pikax_handler.login(username, password)
            from menu import MenuScreen
            go_to_next_screen(src=self, dest=MenuScreen)
        except PikaxException:
            self.login_button.configure(state=NORMAL)
            sys.stdout.write('Login Failed')

    def load(self):

        for index, component in enumerate(self.components):
            component.grid_configure(row=index)
            self.grid(component)

        self.username_entry.focus()
        self.login_button.configure(state=NORMAL)
        self.frame.pack_configure(expand=True)
        self.pack(self.frame)


    def destroy(self):
        self.frame.destroy()
