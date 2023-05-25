from typing import List

class Track:
    def __init__(self, id, name=None, artist=None, album=None, duration_ms=None, popularity=None, acousticness=None, danceability=None, energy=None, instrumentalness=None, key=None, liveness=None, loudness=None, tempo=None, valence=None, year=None, mode=None):
        self.id: str = id
        self.name: str = name
        self.genres: List[str] = []