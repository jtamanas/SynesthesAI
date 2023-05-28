class Track:
    def __init__(
        self,
        **track_data,
    ):
        for key, value in track_data.items():
            setattr(self, key, value)

        self.artist = self.artists[0]
        self.year = int(self.album["release_date"].split("-")[0])

    def add_features(self, **spotify_features):
        """Adds features like tempo, energy, etc."""
        for key, value in spotify_features.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f"{self.name} - {self.artist['name']}"
