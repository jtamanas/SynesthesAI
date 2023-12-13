from typing import List
from music.track import Track
from constants import recommendation_genres, DEFAULT_SEARCH_PARAMETERS

from utils import (
    deep_merge_dicts,
    dict_to_string,
    filter_values,
    fuzzy_filter_values,
    pull_keys_to_top_level,
    remove_default_attributes,
)

# these are attributes that are not meant to be treated like the others
# re: making min, max, and target arguments
SPECIAL_ATTRIBUTES = ["year"]


class Playlist:
    def __init__(self, **playlist_data):
        self.name: str = "The Best Playlist Ever"
        self.seed_genres: List[str] = []
        self.seed_artists: List[str] = []
        self.seed_tracks: List[str] = []
        self.track_list: List[Track] = []

        # Lists are parsed as dictionaries with a values key.
        # Extract the values from these dictionaries
        playlist_data = self.get_lists_from_values(playlist_data)
        playlist_data = self.add_mood_to_genres(playlist_data)
        print(playlist_data)
        # merge with default parameters
        playlist_data = deep_merge_dicts(DEFAULT_SEARCH_PARAMETERS, playlist_data)
        # drop keys that were never specified. They mess up the search
        playlist_data = remove_default_attributes(
            DEFAULT_SEARCH_PARAMETERS, playlist_data, keys_to_keep=["year"]
        )
        top_level_keys = [key for key in DEFAULT_SEARCH_PARAMETERS.keys()]
        pull_keys_to_top_level(playlist_data, top_level_keys)

        print("THIS IS THE TOML AFTER FIXING AND BEFORE LIMITING SEEDS")
        print(playlist_data)

        for key, value in playlist_data.items():
            setattr(self, key, value)
        self.parse_keys()

    def parse_keys(self):
        specified_modes_and_keys = set()
        if hasattr(self, "keys"):
            for key in self.keys:
                # first 0-11 are minor, second 12-23 are major. order of keys is repeated
                mode = key // 12
                key = key % 12
                specified_modes_and_keys.add((mode, key))
        self.min_mode = min(mode for mode, _ in specified_modes_and_keys)
        self.max_mode = max(mode for mode, _ in specified_modes_and_keys)
        self.min_key = min(key for _, key in specified_modes_and_keys)
        self.max_key = max(key for _, key in specified_modes_and_keys)
        self.modes_and_keys = specified_modes_and_keys

    def add_tracks(self, tracks: List[Track]):
        self.track_list.extend(tracks)
        self.filter_tracks_by_genre()
        self.filter_tracks_by_mode_and_key()
        self.sort_playlist_by_tempo()

    def add_mood_to_genres(self, query_dict):
        """
        another way to add genres. We might as well add these to the genre list
        """

        def _add_mood(mood_key, q_dict):
            if mood_key in q_dict:
                if "genres" in q_dict:
                    q_dict["genres"] += q_dict.pop(mood_key)
                else:
                    q_dict["genres"] = q_dict.pop(mood_key)
            return q_dict

        query_dict = _add_mood("mood", q_dict=query_dict)
        query_dict = _add_mood("moods", q_dict=query_dict)
        return query_dict

    def get_lists_from_values(self, dict_with_values_key):
        """
        Takes in a dictionary with keys whose values are dictionaries.
        Some of these sub-dictionaries have a values key with a list of values.
        Extracts the values from these sub-dictionaries and returns a list of them
        to be used as the value for the key in the original dictionary.
        """
        result = {}
        for key, value in dict_with_values_key.items():
            if isinstance(value, dict) and "values" in value:
                result[key] = value["values"]
            else:
                result[key] = value
        return result

    def range_min_max_to_target(self, min_max_dict):
        """Takes in a dictionary with min,max keys. Returns a dictionary with target keys where target=mean(min, max)"""
        return {"target": (min_max_dict["min"] + min_max_dict["max"]) / 2}

    def increase_min_max_range(self, min_max_dict, change_rate=0.05):
        """Takes in a dictionary with min,max keys. Returns a dictionary with target keys and values (min=0.95*min, max=1.05*min)"""
        # max can go above 1.0, but the api can handle this so it's not a problem
        return {
            "min": (1 - change_rate / 2) * min_max_dict["min"],
            "max": (1 + change_rate / 2) * min_max_dict["max"],
        }

    def limit_number_of_seeds(self):
        """
        Spotify limits the number of seeds to 3, so we need to limit the number of seeds.
        Additionally, if more than one seed is given, the playlist will be based on the
        first seed. This is because Spotify will fail if multiple seeds of
        length > 1 are given.
        """

        # Filter genres
        genres = self.genres
        splits = []
        for string in genres:
            splits.extend(string.split())
        genres = genres + splits
        self.seed_genres = filter_values(genres, recommendation_genres)
        if not self.seed_genres:
            self.seed_genres = fuzzy_filter_values(
                genres, recommendation_genres, cutoff=0.6
            )

        # Limit number of seeds
        if len(self.seed_artists) > 1 or len(self.seed_tracks) > 1:
            self.seed_genres = self.seed_genres[:1]
        if len(self.seed_tracks) > 1:
            self.seed_artists = self.seed_artists[:1]

        for key in ["seed_artists", "seed_genres", "seed_tracks"]:
            full_list = getattr(self, key)
            setattr(self, key, full_list[:3])

        if not (self.seed_artists) and not self.seed_genres and self.seed_tracks:
            print("NO ARTISTS, TRACKS, OR GENRES RETURNED")

    def generate_query(self):
        self.limit_number_of_seeds()
        playlist_query = self.__dict__
        return playlist_query

    def generate_playlist_query_with_ranges(self):
        new_search_dict = {}
        for key, val in self.generate_query().items():
            if isinstance(val, dict) and key not in SPECIAL_ATTRIBUTES:
                for range_key, range_val in val.items():
                    new_search_dict[f"{range_key}_{key}"] = range_val
            else:
                new_search_dict[key] = self.generate_query()[key]
        return new_search_dict

    def generate_playlist_query_with_increased_range(self):
        """Assumes it gets {other:val, ..., min_key:, max_key:, min_key1:, max_key1:, ...}"""
        new_query_dict = {}
        for key, val in self.generate_query().items():
            SKIP_THESE_KEYS = ["year", "tempo"]
            if isinstance(val, dict) and key not in SKIP_THESE_KEYS:
                try:
                    if val["max"] == 0:
                        # If 0, it can never be increased. Nudge it up so it can be increased
                        val["max"] = 0.01
                    new_query_dict[key] = self.increase_min_max_range(val)
                except:
                    print(f"DROPPED {key} BECAUSE IT LACKED VALID MIN/MAX KEYS")
                    pass
            else:
                new_query_dict[key] = val
        return new_query_dict

    def filter_genres(self, genre_names):
        remaining = [
            genre.lower()
            for genre in genre_names
            if genre.lower() in recommendation_genres
        ]
        if not remaining:
            print("NO VALID GENRES RETURNED!")
            print("BUT WE GOT THESE GENRES")
            print(genre_names)
        return remaining

    def find_artist(self, artist_id):
        uri = f"spotify:artist:{artist_id}"
        return self.spotify_handler.spotify.artist(uri)

    def filter_tracks_by_category(self, tracks: List[Track], category_range):
        filtered_tracks = []
        for track in tracks:
            if category_range["min"] <= track.year <= category_range["max"]:
                filtered_tracks.append(track)
        return filtered_tracks

    def filter_tracks_by_mode_and_key(self):
        filtered_tracks = []
        if self.track_list and self.modes_and_keys:
            for track in self.track_list:
                if hasattr(track, "key") and hasattr(track, "mode") and track.key != -1:
                    # -1 means spotify did not assign a key to the track
                    if (track.mode, track.key) in self.modes_and_keys:
                        filtered_tracks.append(track)
                else:
                    filtered_tracks.append(track)

        # Print a message stating which tracks were dropped
        dropped_tracks = [
            track for track in self.track_list if track not in filtered_tracks
        ]
        if dropped_tracks:
            print(f"The following tracks were dropped bc of keys: {dropped_tracks}")

        print("TEST")
        print("HERE ARE THE TRACKS' (MODE, KEY)")
        print([(track.mode, track.key) for track in filtered_tracks])
        self.track_list = filtered_tracks

    def filter_tracks_by_genre(self):
        """
        The first track sets the tone of the playlist.
        Make sure that all tracks share genres with the original track.
        """
        if self.track_list:
            # Get the genres of the first track
            idx = 0
            reference_track_genres = []
            while not reference_track_genres and idx < len(self.track_list):
                # sometimes the tracks lack genres. in this case, just get the next available
                #! we'll end up dropping the genre-less tracks.
                reference_track_genres = self.track_list[idx].all_genres
                idx += 1

            if reference_track_genres:
                # Filter the tracks to only those that share genres with the first track
                filtered_tracks = [
                    track
                    for track in self.track_list
                    if any(
                        genre in track.all_genres for genre in reference_track_genres
                    )
                ]

                # Print a message stating which tracks were dropped
                dropped_tracks = [
                    track for track in self.track_list if track not in filtered_tracks
                ]
                if dropped_tracks:
                    print(
                        f"The following tracks were dropped bc of genre: {dropped_tracks}"
                    )

                self.track_list = filtered_tracks

    def __repr__(self) -> str:
        return dict_to_string(self.__dict__)

    def sort_playlist_by_tempo(self):
        """
        Sorts the playlist by tempo, with the first song staying in its place.

        First, the remaining songs are sorted by tempo in ascending order.
        Then, they are split into two lists:
            one for songs with tempo less than the first song's tempo,
            and another for songs with tempo greater than or equal to the first song's tempo.
            Each of these two sublists is then split again in half (by skipping indices)


        The list with the shorter length is then merged with the first song,
            Before it is, however, it is split in half (by alternating indices)
                Its second subsublist is reverse ordered and recombined with the first subsublist

        followed by the other list in the opposite order.
        """

        def _from_sorted_to_local_extremum(l):
            even_list = l[::2]
            odd_list = l[1::2]
            l = even_list + list(reversed(odd_list))
            return l

        if self.track_list:
            first_song = self.track_list[0]
            remaining_songs = sorted(self.track_list[1:], key=lambda x: x.tempo)

            less_tempo = [
                song for song in remaining_songs if song.tempo < first_song.tempo
            ]
            greater_or_equal_tempo = [
                song for song in remaining_songs if song.tempo >= first_song.tempo
            ]

            less_tempo = sorted(less_tempo, key=lambda x: x.tempo, reverse=True)
            greater_or_equal_tempo = sorted(
                greater_or_equal_tempo, key=lambda x: x.tempo
            )
            if len(less_tempo) < len(greater_or_equal_tempo):
                less_tempo = _from_sorted_to_local_extremum(less_tempo)

                smoothed_track_list = [first_song] + less_tempo + greater_or_equal_tempo
            else:
                greater_or_equal_tempo = _from_sorted_to_local_extremum(
                    greater_or_equal_tempo
                )

                smoothed_track_list = [first_song] + greater_or_equal_tempo + less_tempo

            print([t.tempo for t in smoothed_track_list])
            self.track_list = smoothed_track_list
