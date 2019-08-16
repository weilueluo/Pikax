from .exceptions import PikaxResultError
from .api.models import Artwork
from .models import PikaxResult


class DefaultPikaxResult(PikaxResult):

    def __init__(self, artworks, download_type, folder=''):
        super().__init__(artworks, download_type, folder)

    def result_maker(self, artworks, download_type, folder):
        return DefaultPikaxResult(artworks, download_type, folder)

    def __add__(self, other: 'PikaxResult') -> 'PikaxResult':
        if self._download_type is not other.download_type:
            raise PikaxResultError(
                f'PikaxResults are in different type: {self._download_type} and {other.download_type}')
        new_artworks = list(set(self.artworks + other.artworks))
        new_folder = self.folder + '_added_to_' + other.folder
        return DefaultPikaxResult(artworks=new_artworks, download_type=self._download_type, folder=new_folder)

    def __sub__(self, other: 'PikaxResult') -> 'PikaxResult':
        if self._download_type is not other.download_type:
            raise PikaxResultError(
                f'PikaxResults are in different type: {self._download_type} and {other.download_type}')
        new_artworks = [artwork for artwork in self.artworks if artwork not in other.artworks]
        new_folder = self.folder + '_subbed_by_' + other.folder
        return DefaultPikaxResult(new_artworks, download_type=self._download_type, folder=new_folder)

    def __getitem__(self, index: int) -> Artwork:
        return self.artworks[index]

    def __len__(self) -> int:
        return len(self.artworks)
