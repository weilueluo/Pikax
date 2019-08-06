from .. import util


class ClientInterface:

    def bookmarks(self, limit) -> list: raise NotImplementedError

    def illusts(self, limit) -> list: raise NotImplementedError

    def novels(self, limit) -> list: raise NotImplementedError

    def mangas(self, limit) -> list: raise NotImplementedError


class PagesInterface:

    def search(self, limit) -> list: raise NotImplementedError

    def rank(self, limit) -> list: raise NotImplementedError
