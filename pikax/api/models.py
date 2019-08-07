from .. import util


class PikaxResultInterface:
    ...


class PikaxResult(PikaxResultInterface):
    ...


class PikaxUserInterface:

    def bookmarks(self, limit: int) -> PikaxResult: raise NotImplementedError

    def illusts(self, limit: int) -> PikaxResult: raise NotImplementedError

    def novels(self, limit: int) -> PikaxResult: raise NotImplementedError

    def mangas(self, limit: int) -> PikaxResult: raise NotImplementedError


class PikaxPagesInterface:

    def search(self, limit: int) -> PikaxResult: raise NotImplementedError

    def rank(self, limit: int) -> PikaxResult: raise NotImplementedError


class UserInterface:

    def bookmarks(self, limit: int) -> list: raise NotImplementedError

    def illusts(self, limit: int) -> list: raise NotImplementedError

    def novels(self, limit: int) -> list: raise NotImplementedError

    def mangas(self, limit: int) -> list: raise NotImplementedError


class PagesInterface:

    def search(self, limit: int) -> list: raise NotImplementedError

    def rank(self, limit: int) -> list: raise NotImplementedError
