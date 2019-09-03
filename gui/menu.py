import tkinter as tk

import texts
from common import go_to_next_screen
from models import PikaxGuiComponent


class MenuScreen(PikaxGuiComponent):
    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

        self.grid_height = 10
        self.grid_width = 1

        # create buttons
        self.rank_button = self.make_button(text=texts.MENU_RANK)
        self.id_button = self.make_button(text=texts.MENU_ID)
        self.search_button = self.make_button(text=texts.MENU_SEARCH)
        self.back_button = self.make_button(text=texts.MENU_BACK)

        self.rank_button_id = self.add_widget(widget=self.rank_button, row=3)
        self.id_button_id = self.add_widget(widget=self.id_button, row=4)
        self.search_button_id = self.add_widget(widget=self.search_button, row=5)
        self.back_button_id = self.add_widget(widget=self.back_button, row=7)

        self.buttons = [
            self.rank_button,
            self.id_button,
            self.search_button,
            self.back_button
        ]

        self.config_buttons()
        self.frame.pack_configure(expand=True)
        self.pack(self.frame)

    def config_buttons(self):
        self.search_button.configure(command=self.search_clicked)
        self.rank_button.configure(command=self.rank_clicked)
        self.id_button.configure(command=self.id_clicked)
        self.back_button.configure(command=self.back_clicked)
        if not self.pikax_handler.logged:
            self.search_button.configure(state=tk.DISABLED)

    def id_clicked(self):
        from id import IdScreen
        go_to_next_screen(src=self, dest=IdScreen)

    def rank_clicked(self):
        from rank import RankScreen
        go_to_next_screen(src=self, dest=RankScreen)

    def search_clicked(self):
        from search import SearchScreen
        go_to_next_screen(src=self, dest=SearchScreen)

    def back_clicked(self):
        from login import LoginScreen
        go_to_next_screen(src=self, dest=LoginScreen)


def main():
    from pikaxhandler import PikaxHandler
    root = tk.Tk()
    MenuScreen(root, pikax_handler=PikaxHandler())
    root.mainloop()


if __name__ == '__main__':
    main()
