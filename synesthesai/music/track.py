class Track:
    def __init__(
        self,
        **track_data,
    ):
        for key, value in track_data.items():
            setattr(self, key, value)

        self.artist = self.artists[0]["name"]
        self.year = int(self.album["release_date"].split("-")[0])

    def __repr__(self) -> str:
        return f"{self.name} - {self.artist}"
