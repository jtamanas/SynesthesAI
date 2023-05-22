class Playlist:
    def __init__(self, name=None, tracks=None):
        self.name = name
        self.tracks = tracks or []

    def add_track(self, track):
        if not any(existing_track.id == track.id for existing_track in self.tracks):
            self.tracks.append(track)

    def remove_track(self, track):
        self.tracks.remove(track)

    def get_track_names(self):
        return [track.name for track in self.tracks]

    def get_track_artists(self):
        return [track.artist for track in self.tracks]

    def get_track_durations(self):
        return [track.duration_ms for track in self.tracks]

    def get_track_popularities(self):
        return [track.popularity for track in self.tracks]