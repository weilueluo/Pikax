from threading import Thread
from tkinter import *
from tkinter import font

from PIL import Image, ImageTk

import settings
from common import go_to_next_screen
from lib.pikax.exceptions import PikaxException
from models import PikaxGuiComponent


class LoginScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        # settings
        self.grid_height = 20
        self.grid_width = 2
        self.text_color = '#7d2c40'
        self.entry_color = '#b54a65'
        self.entry_text_color = 'white'
        self.cursor_color = 'white'

        # add background and text
        self.background = self.add_background(image_path=settings.LOGIN_BACKGROUND_PATH)
        title_font = font.Font(family=settings.DEFAULT_FONT_FAMILY, size=20, weight=font.BOLD)
        self.canvas_title = self.add_text(text=settings.TITLE, font=title_font, row=3)
        self.canvas_username = self.add_text(text='username', row=7)
        self.canvas_password = self.add_text(text='password', row=10)

        # make entries & button
        self.username_entry = self.make_entry()
        self.password_entry = self.make_entry()
        self.config_entries([self.username_entry, self.password_entry])
        self.output = self.make_entry()
        self.login_button = self.make_button(text='login')

        # add entries & button to canvas
        self.username_entry_id = self.add_widget(canvas=self.background, widget=self.username_entry, row=8)
        self.password_entry_id = self.add_widget(canvas=self.background, widget=self.password_entry, row=11)
        self.login_button_id = self.add_widget(canvas=self.background, widget=self.login_button, row=13)
        self.output_id = self.add_widget(canvas=self.background, widget=self.output, row=15)

        self.config_texts([self.canvas_title, self.canvas_username, self.canvas_password])

        self.config_login_button()
        self.config_output()

        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

    def config_texts(self, texts):
        for item in texts:
            self.background.itemconfigure(item, fill=self.text_color)

    def add_text(self, text, font=None, row=0, **kwargs):
        if not font:
            font = self.label_font
        return super().add_text(canvas=self.background, text=text, font=font, row=row)

    def add_background(self, image_path):
        im = Image.open(image_path).resize((self.width, self.height))
        im = ImageTk.PhotoImage(im)
        background = self.make_fullscreen_canvas()
        background.create_image((0, 0), image=im, anchor=NW)
        background.image = im  # keep a reference prevent gc-ed
        self.grid(background, row=0, column=0, rowspan=self.grid_height, columnspan=self.grid_width)
        return background

    def config_output(self):
        self.output.configure(state=DISABLED, justify=CENTER, width=60)
        self.redirect_output_to(self.output)

    def config_login_button(self):
        self.login_button.configure(command=self.login)

    def config_entries(self, entries):
        self.username_entry.bind('<Return>', self.login)
        self.password_entry.bind('<Return>', self.login)
        self.password_entry.configure(show="\u2022")  # bullet
        for item in entries:
            item.configure(bg=self.entry_color, fg=self.entry_text_color,
                           insertbackground=self.cursor_color, font=self.entry_font)

    # def config_labels(self):
    #     self.title_label.configure(font="-weight bold", anchor=CENTER)
    #     self.contact_label.configure(bg='grey95', fg='grey50')
    #     self.contact_label.configure(state=NORMAL)
    #     self.contact_label.tag_configure("center", justify=CENTER)
    #     self.contact_label.insert(0.0, 'Issue? report @ https://github.com/Redcxx/Pikax/issues')
    #     self.contact_label.tag_add("center", "1.0", "end")
    #     self.contact_label.configure(state=DISABLED)

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

    def destroy(self):
        self.frame.destroy()
