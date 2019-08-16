from factory import make_label, make_entry, make_button, NORMAL, pack, CENTER, BOTTOM, make_text, DISABLED
from lib.pikax.exceptions import PikaxException

from models import PikaxGuiComponent
from common import go_to_next_screen, StdoutRedirector
import sys


class LoginScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.title_label = make_label(self.frame, text='Pikax')
        self.title_label.configure(font="-weight bold", anchor=CENTER)
        self.username_label = make_label(self.frame, text='username')
        self.password_label = make_label(self.frame, text='password')
        self.username_entry = make_entry(self.frame)
        self.password_entry = make_entry(self.frame)
        self.login_button = make_button(self.frame, text='login')
        self.login_button.configure(command=self.login)
        self.username_entry.bind('<Return>', self.login)
        self.password_entry.bind('<Return>', self.login)
        self.output_text = make_entry(self.frame)
        self.output_text.configure(state=DISABLED, justify=CENTER)
        sys.stdout = StdoutRedirector(self.output_text)
        self.load()

    def login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            self.pikax_handler.login(username, password)
            from menu import MenuScreen
            go_to_next_screen(src=self, dest=MenuScreen)
        except PikaxException:
            print('Login Failed')

    def load(self):
        self.frame.pack_configure(expand=True)
        self.output_text.pack_configure(side=BOTTOM, expand=True)

        pack(self.title_label)
        pack(self.username_label)
        pack(self.username_entry)
        pack(self.password_label)
        pack(self.password_entry)
        pack(self.login_button)
        pack(self.output_text)
        pack(self.frame)

        self.username_entry.focus()
        self.login_button.configure(state=NORMAL)

    def destroy(self):
        self.frame.destroy()
