from models import PikaxGuiComponent


class RankScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)

    def load(self):
        ...

    def destroy(self):
        ...
