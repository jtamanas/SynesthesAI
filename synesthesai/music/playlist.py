from typing import List
from music.track import Track
from constants import recommendation_genres, DEFAULT_SEARCH_PARAMETERS

from utils import (
    deep_merge_dicts,
    dict_to_string,
    filter_values,
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

        # playlist_data = self.limit_number_of_seeds_and_get_ids(playlist_data)

        for key, value in playlist_data.items():
            setattr(self, key, value)

    def add_mood_to_genres(self, query_dict):
        """
        PaLM especially likes to add a "mood" dictionary. Oftentimes, this is just
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

    def limit_number_of_seeds(self):
        """
        Spotify limits the number of seeds to 3, so we need to limit the number of seeds.
        Additionally, if more than one seed is given, the playlist will be based on the
        first seed. This is because Spotify will fail if multiple seeds of
        length > 1 are given.
        """

        # Filter genres
        self.seed_genres = filter_values(self.genres, recommendation_genres)

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

    def generate_playlist_query_with_targets(self):
        """Assumes it gets {other:val, ..., min_key:, max_key:, min_key1:, max_key1:, ...}"""
        new_query_dict = {}
        for key, val in self.generate_query().items():
            if isinstance(val, dict) and key not in SPECIAL_ATTRIBUTES:
                try:
                    new_query_dict[key] = self.range_min_max_to_target(val)
                except:
                    print(f"DROPPED {key} BECAUSE IT LACKED MIN/MAX KEYS")
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

    def __repr__(self) -> str:
        return dict_to_string(self.__dict__)
