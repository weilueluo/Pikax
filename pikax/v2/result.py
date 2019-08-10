import operator
import os

from ..api.models import Artwork
from .models import PikaxResult


class DefaultPikaxResult(PikaxResult):

    def __init__(self, artworks, folder=''):
        super().__init__(artworks, folder)

    def __add__(self, other: 'PikaxResult') -> 'PikaxResult':
        new_artworks = list(set(self.artworks + other.artworks))
        new_folder = self.folder + '_added_to_' + other.folder
        return DefaultPikaxResult(new_artworks, new_folder)

    def __sub__(self, other: 'PikaxResult') -> 'PikaxResult':
        new_artworks = [artwork for artwork in self.artworks if artwork not in other.artworks]
        new_folder = self.folder + '_subbed_by_' + other.folder
        return DefaultPikaxResult(new_artworks, new_folder)

    def __getitem__(self, index: int) -> Artwork:
        return self.artworks[index]

    def __len__(self) -> int:
        return len(self.artworks)
