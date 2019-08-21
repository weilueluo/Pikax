from factory import make_button, NORMAL, pack
from models import PikaxGuiComponent
from common import go_to_next_screen


class MenuScreen(PikaxGuiComponent):
    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.search_button = self.make_button(text='Search')
        self.search_button.configure(command=self.search_clicked)
        self.rank_button = self.make_button(text='Rank')
        self.rank_button.configure(command=self.rank_clicked)
        self.id_button = self.make_button('ID')
        self.id_button.configure(command=self.id_clicked)
        self.back_button = self.make_button(text='Back')
        self.back_button.configure(command=self.back_clicked)

        self.buttons = [
            self.search_button,
            self.rank_button,
            self.id_button,
            self.back_button
        ]

        self.load()

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

    def load(self):

        for button in self.buttons:
            self.pack(button)
            button.configure(state=NORMAL)

        self.frame.pack_configure(expand=True)
        pack(self.frame)

    def destroy(self):
        self.frame.destroy()


def main():
    from pikaxhandler import PikaxHandler
    import tkinter as tk
    root = tk.Tk()
    MenuScreen(root, pikax_handler=PikaxHandler())
    root.mainloop()


if __name__ == '__main__':
    main()
