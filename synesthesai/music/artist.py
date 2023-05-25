from typing import List
from utils import fuzzy_filter_values
from constants import recommendation_genres


class Artist:
    def __init__(self, **artist_data):
        for key, value in artist_data.items():
            setattr(self, key, value)

        self.genres = list(set(fuzzy_filter_values(self.genres, recommendation_genres)))

    def __repr__(self) -> str:
        return self.name
