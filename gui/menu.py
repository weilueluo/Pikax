from factory import make_button, NORMAL, pack
from models import PikaxGuiComponent
from common import go_to_next_screen


class MenuScreen(PikaxGuiComponent):
    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.search_button = make_button(self.frame, text='search')
        self.rank_button = make_button(self.frame, text='rank')
        self.rank_button.configure(command=self.rank_clicked)
        self.search_button = make_button(self.frame, text='search')
        self.search_button.configure(command=self.search_clicked)
        self.back_button = make_button(self.frame, text='back')
        self.back_button.configure(command=self.back_clicked)
        self.load()

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
        self.frame.pack_configure(expand=True)

        pack(self.search_button)
        pack(self.rank_button)
        pack(self.back_button)
        pack(self.frame)

        self.search_button.configure(state=NORMAL)
        self.rank_button.configure(state=NORMAL)
        self.search_button.configure(state=NORMAL)
        self.back_button.configure(state=NORMAL)

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
