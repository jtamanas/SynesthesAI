import streamlit as st
from constants import DEFAULT_SEARCH_PARAMETERS, recommendation_genres
from prompts.shared_elements import beginning_of_toml
import random
from utils import deep_merge_dicts, pull_keys_to_top_level, remove_default_attributes, partial_load_toml
import tomllib as toml
from LLM.openai import OpenAI
from LLM.palm import PaLM

# these are attributes that are not meant to be treated like the others
# re: making min, max, and target arguments
SPECIAL_ATTRIBUTES = ["year"]


class PlaylistHandler:
    def __init__(self, spotify_handler):
        self.spotify_handler = spotify_handler
        self.LLM = PaLM(model="models/text-bison-001")
        # self.LLM = OpenAI(model="text-davinci-003")
        self.max_tokens = 350
        self.temperature = 1.0

    def get_lists_from_values(self, dict_with_values_key):
        """
        Takes in a dictionary with keys whose values are dictionaries. 
        Some of these sub-dictionaries have a values key with a list of values.
        Extracts the values from these sub-dictionaries and returns a list of them
        to be used as the value for the key in the original dictionary.
        """
        result = {}
        for key, value in dict_with_values_key.items():
            if isinstance(value, dict) and 'values' in value:
                result[key] = value['values']
            else:
                result[key] = value
        return result

    # your methods like get_recommendation_parameters, filter_genres, get_track_recommendations etc.
    def range_min_max_to_target(self, min_max_dict):
        """Takes in a dictionary with min,max keys. Returns a dictionary with target keys where target=mean(min, max)"""
        return {"target": (min_max_dict["min"] + min_max_dict["max"]) / 2}

    def get_playlist_query_with_targets(self, query_dict):
        """Assumes it gets {other:val, ..., min_key:, max_key:, min_key1:, max_key1:, ...}"""
        new_query_dict = {}
        for key, val in query_dict.items():
            if isinstance(val, dict) and key not in SPECIAL_ATTRIBUTES:
                try:
                    new_query_dict[key] = self.range_min_max_to_target(val)
                except:
                    print(f"DROPPED {key} BECAUSE IT LACKED MIN/MAX KEYS")
                    pass
            else:
                new_query_dict[key] = val
        return new_query_dict

    def get_recommendation_parameters(self, prompt, debug=True):
        try:
            if debug:
                generated_toml = """
playlist_name = "[TEST] Starry Night Vibes"
[genres]
values = ["classical", "ambient"]

[energy]
min = 0
max = 0.3

[danceability]
min = 0
max = 0.3

[valence]
min = 0.6
max = 0.9

[acousticness]
min = 0.7
max = 1

[year]
min = 1988
max = 2002

[artists]
values = ["Ludovico - Einaudi", "Nujabes", "Gustavo Santaolalla", "Hans Zimmer"]

[tracks]
values = [
  "Someone You Loved by Lewis Capaldi",
  "When the Party's Over by Billie Eilish",
  "Love Me Now by John Legend"
]
[broken]
values = [
                """
            else:
                # Send the prompt to the OpenAI API
                generated_toml = self.LLM.complete(
                    prompt=prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                print("THIS IS THE LLM RESPONSE")
                print(generated_toml)
                # Extract the generated TOML from the response
                generated_toml = beginning_of_toml + generated_toml
                # Trim out "---" from the beginning and end if they exist
                # the longest string is the one we want
                generated_toml = generated_toml.split("---\n")
                generated_toml = max(generated_toml, key=len)
                # do the same with ``` if it exist`
                generated_toml = generated_toml.split("```")
                generated_toml = max(generated_toml, key=len)
                print(generated_toml)

            try:
                playlist_data = toml.loads(generated_toml)
            except Exception as e:
                print("TOML IS BROKEN. LOADING PARTIAL")
                playlist_data = partial_load_toml(generated_toml)

            # Lists are parsed as dictionaries with a values key. 
            # Extract the values from these dictionaries
            playlist_data = self.get_lists_from_values(playlist_data)
            print("THIS IS THE TOML IMMEIDATELY AFTER PARSING")
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

            playlist_data = self.limit_number_of_seeds(playlist_data)

        except Exception as e:
            print(f"Unexpected error in get_recommendation_parameters: {e}")
            raise

        print("THIS IS THE TOML AT THE END OF THE FUNCTION")
        print(playlist_data)

        return playlist_data
    
    def limit_number_of_seeds(self, query_dict):
        """
        Spotify limits the number of seeds to 3, so we need to limit the number of seeds.
        Additionally, if more than one seed is given, the playlist will be based on the 
        first seed. This is because Spotify will fail if multiple seeds of 
        length > 1 are given.
        """

        # Filter genres
        if "genres" in query_dict:
            query_dict["seed_genres"] = self.filter_genres(query_dict["genres"])

        # Get artist IDs
        artist_ids = []
        if "artists" in query_dict:
            artist_ids = self.get_ids_from_search(
                names=query_dict["artists"],
                years=query_dict["year"],
                search_type="artist",
            )
            query_dict["seed_artists"] = artist_ids

        # Get track IDs
        track_ids = []
        if "tracks" in query_dict:
            track_ids = self.get_ids_from_search(
                names=query_dict["tracks"],
                years=query_dict["year"],
                search_type="track",
            )
            query_dict["seed_tracks"] = track_ids


        # Limit number of seeds
        if artist_ids or track_ids:
            query_dict["seed_genres"] = query_dict.get("seed_genres", [])[:1]
        if track_ids:
            query_dict["seed_artists"] = query_dict.get("seed_artists", [])[:1]

        for key in ["seed_artists", "seed_genres", "seed_tracks"]:
            if key in query_dict:
                query_dict[key] = query_dict[key][:3]

        return query_dict

    def get_playlist_query_with_ranges(self, spotify_search_dict: dict):
        new_search_dict = {}
        for key, val in spotify_search_dict.items():
            if isinstance(val, dict) and key not in SPECIAL_ATTRIBUTES:
                for range_key, range_val in val.items():
                    new_search_dict[f"{range_key}_{key}"] = range_val
            else:
                new_search_dict[key] = spotify_search_dict[key]
        return new_search_dict

    def filter_genres(self, genre_names):
        remaining = []
        for genre in genre_names:
            genre = genre.lower()
            if genre in recommendation_genres:
                remaining.append(genre)
        if not remaining:
            print(genre_names)
            raise ValueError("No genres returned!")
        return remaining

    def find_artist(self, artist_id):
        uri = f"spotify:artist:{artist_id}"
        return self.spotify_handler.spotify.artist(uri)

    def get_ids_from_search(self, names, years, search_type="artist"):
        """search_type can be artist or tracks currently"""
        print(f"getting {search_type} ids")
        pieces = []
        for name in names:
            print(name)
            result = self.spotify_handler.spotify.search(
                f"{name} year:{years['min']}-{years['max']}", type=search_type, limit=1
            )
            if result[f'{search_type}s']['items']:
                print(
                    f"Searched for {name}, found: {result[f'{search_type}s']['items'][0]['name']}"
                )
                pieces.append(result[f"{search_type}s"]["items"][0]["id"])
        return pieces

    def filter_tracks_by_category(self, tracks, category_range):
        filtered_tracks = []
        for track in tracks:
            year = int(track["album"]["release_date"].split("-")[0])
            if category_range["min"] <= year <= category_range["max"]:
                filtered_tracks.append(track)
        return filtered_tracks

    def get_track_recommendations(self, genres=[""], limit=10, **kwargs):
        """I pull out genres from kwargs to ensure it doesnt mess up the search"""
        tracks = self.spotify_handler.spotify.recommendations(limit=limit, **kwargs)[
            "tracks"
        ]
        tracks = self.spotify_handler.spotify.recommendations(limit=limit, **kwargs)[
            "tracks"
        ]
        # filter by year, ensuring only relevant tracks are added
        tracks = self.filter_tracks_by_category(
            tracks,
            category_range=kwargs["year"],
        )
        track_names = [
            f'{track["name"]} - {track["artists"][0]["name"]}' for track in tracks
        ]
        track_ids = [track["id"] for track in tracks]
        track_ids = list(set(track_ids))
        print("\n".join(track_names))
        # sometimes recommendations returns more than the limit for some reason
        return track_ids[-limit:]

    def add_tracks_to_queue(self, track_ids):
        for track_id in track_ids:
            self.spotify_handler.spotify.add_to_queue(f"spotify:track:{track_id}")
        print("Tracks added to the queue successfully!")

    def get_track_uris(self, track_ids):
        return [f"spotify:track:{track_id}" for track_id in track_ids]

    def create_spotify_playlist(
        self, username, track_ids, playlist_name="Test", music_request=""
    ):
        playlist = self.spotify_handler.spotify.user_playlist_create(
            username,
            playlist_name,
            public=True,
            description=music_request,
        )
        playlist_url = playlist["external_urls"]["spotify"]
        playlist_url = (
            '<a target="_blank" href="{url}" >Now on Spotify: {msg}</a>'.format(
                url=playlist_url, msg=playlist_name
            )
        )
        st.markdown(playlist_url, unsafe_allow_html=True)
        playlist_id = playlist["id"]
        track_uris = self.get_track_uris(track_ids)
        print(track_uris)
        self.spotify_handler.spotify.playlist_add_items(playlist_id, track_uris)
        print(f"Playlist '{playlist_name}' created and tracks added successfully!")
        return playlist_id

    def set_playlist_cover_image(self, playlist_id, image_b64):
        try:
            self.spotify_handler.spotify.playlist_upload_cover_image(
                playlist_id, image_b64
            )
            print("Uploaded playlist cover photo")
        except Exception as e:
            print("FAILED to upload playlist photo")
            print(e)

    def get_seed_tracks_query(self, playlist_data, track_ids, n=5):
        random_tracks = random.sample(track_ids, min(n, len(track_ids)))
        for key in ["seed_genres", "seed_artists", "seed_tracks"]:
            if key in playlist_data:
                playlist_data.pop(key)
        playlist_data["seed_tracks"] = [track for track in random_tracks]
        return playlist_data

    def generate_playlist(
        self,
        username,
        prompt,
        music_request=None,
        debug=False,
        num_tracks=20,
        num_enhanced_tracks_to_add=3,
    ):
        music_request = music_request or ""
        formatted_prompt = prompt.format(
            beginning_of_toml=beginning_of_toml, music_request=music_request
        )
        raw_playlist_query = self.get_recommendation_parameters(
            formatted_prompt, debug=debug
        )
        print("Got playlist parameters")
        range_playlist_query = self.get_playlist_query_with_ranges(raw_playlist_query)

        playlist_query = range_playlist_query

        # even if there are enough songs in the filter, the vibe of the playlist
        # tends to wander. By limiting the number of tracks from the initial
        # query, we can limit the vibe to just the first n songs
        # start with one song unless seed track is specified.
        track_ids = self.get_track_recommendations(
            limit=1, **playlist_query
        )
        print("Number of tracks: ", len(track_ids))
        while len(track_ids) < num_tracks:
            print("Enhancing the playlist...")
            if track_ids:
                playlist_query = self.get_seed_tracks_query(
                    playlist_query, track_ids
                )
            new_track_ids = self.get_track_recommendations(
                limit=num_enhanced_tracks_to_add, **playlist_query
            )
            unique_new_tracks = [trk_id for trk_id in new_track_ids if trk_id not in track_ids]
            if not unique_new_tracks:
                # if there are no more songs in the fixed ranges, make them targets
                print("NO MORE TRACKS IN RANGE. SWITCHING TO TARGETS")
                playlist_query = self.get_playlist_query_with_targets(
                    raw_playlist_query
                )
            track_ids.extend(unique_new_tracks)
            print("Number of tracks: ", len(track_ids))
        print("Got track ids")

        if "playlist_name" in raw_playlist_query:
            playlist_name = raw_playlist_query["playlist_name"]
        else:
            playlist_name = "For your mood"

        playlist_id = self.create_spotify_playlist(
            username,
            track_ids,
            playlist_name=playlist_name,
            music_request=music_request,
        )
        print("Made the playlist")
        st.balloons()
        return raw_playlist_query, playlist_id
