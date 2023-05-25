class Track:
    def __init__(
        self,
        id,
        name=None,
        artist=None,
        album=None,
        duration_ms=None,
        popularity=None,
        acousticness=None,
        danceability=None,
        energy=None,
        instrumentalness=None,
        key=None,
        liveness=None,
        loudness=None,
        tempo=None,
        valence=None,
        year=None,
        mode=None,
    ):
        self.id = id
        self.name = name
        self.artist = artist
        self.album = album
        self.duration_ms = duration_ms
        self.popularity = popularity
        self.acousticness = acousticness
        self.danceability = danceability
        self.energy = energy
        self.instrumentalness = instrumentalness
        self.key = key
        self.liveness = liveness
        self.loudness = loudness
        self.tempo = tempo
        self.valence = valence
        self.year = year
        self.mode = mode
