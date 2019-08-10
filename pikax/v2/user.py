from pikax import params
from pikax.v2.models import PikaxResult
from .models import PikaxUserInterface
from ..api.processor import DefaultIDProcessor


class DefaultPikaxUser(PikaxUserInterface):

    def __init__(self, client, user_id):
        self.user = client.visit(user_id=user_id)
        self.id_processor = DefaultIDProcessor()

    def illusts(self, limit: int = None) -> PikaxResult:
        ids = self.user.illusts(limit=limit)

    def novels(self, limit: int = None) -> PikaxResult:
        pass

    def mangas(self, limit: int = None) -> PikaxResult:
        pass

    def bookmarks(self, limit: int = None, type: params.Type = params.Type.ILLUST) -> PikaxResult:
        pass
