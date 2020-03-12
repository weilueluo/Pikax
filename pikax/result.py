from . import params

from .api.models import Artwork
from .exceptions import PikaxResultError
from .models import PikaxResult
from .texts import texts

__all__ = ['DefaultPikaxResult']


class DefaultPikaxResult(PikaxResult):

    def __init__(self, artworks, download_type, folder=''):
        super().__init__(artworks, download_type, folder)
        self.allow_mix_types = [params.DownloadType.MANGA, params.DownloadType.ILLUST]

    # workaround for gui to change artworks in PikaxResult
    def renew_artworks(self, new_artworks):
        return DefaultPikaxResult(new_artworks, download_type=self.download_type, folder=self.folder)

    def result_maker(self, artworks, download_type, folder):
        return DefaultPikaxResult(artworks, download_type, folder)

    def _check_type(self, other):
        if self.download_type is not other.download_type \
                and (other.download_type not in self.allow_mix_types
                     or self.download_type not in self.allow_mix_types):
            raise PikaxResultError(texts.INCOMPATIBLE_TYPE_OPERATION.format(type1=self.download_type,
                                                                            type2=other.download_type))

    def __add__(self, other: 'PikaxResult') -> 'PikaxResult':
        self._check_type(other)
        new_artworks = list(set(self.artworks + other.artworks))
        new_folder = self.folder + texts.ADD_FOLDER_CONNECT + other.folder
        return DefaultPikaxResult(artworks=new_artworks, download_type=self.download_type, folder=new_folder)

    def __sub__(self, other: 'PikaxResult') -> 'PikaxResult':
        self._check_type(other)
        new_artworks = [artwork for artwork in self.artworks if artwork not in other.artworks]
        new_folder = self.folder + texts.SUB_FOLDER_CONNECT + other.folder
        return DefaultPikaxResult(new_artworks, download_type=self.download_type, folder=new_folder)

    def __getitem__(self, index: int) -> Artwork:
        return self.artworks[index]

    def __len__(self) -> int:
        return len(self.artworks)

