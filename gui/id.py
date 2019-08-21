from models import PikaxGuiComponent


class IdScreen(PikaxGuiComponent):

    def __init__(self, master, pikax_handler):
        super().__init__(master, pikax_handler)
        self.id_or_url_label = self.make_label('Id or url here')
        self.id_or_url_entry = self.make_entry()
        ...

    def load(self):
        ...

    def destroy(self):
        ...
