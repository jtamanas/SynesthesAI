import streamlit as st
import openai
from spotify_handler import SpotifyHandler
from genre_prompt import beginning_of_json, prompt
from available_genres import recommendation_genres
import json
import random


class PlaylistGenerator:
    def __init__(self, spotify_handler):
        self.spotify_handler = spotify_handler

    # your methods like get_recommendation_parameters, filter_genres, get_track_recommendations etc.
    def range_min_max_to_target(self, min_max_dict):
        """Takes in a dictionary with min,max keys. Returns a dictionary with target keys where target=mean(min, max)"""
        return {"target": (min_max_dict["min"] + min_max_dict["max"]) / 2}

    def get_playlist_query_with_targets(self, query_dict):
        """Assumes it gets {other:val, ..., min_key:, max_key:, min_key1:, max_key1:, ...}"""
        new_query_dict = {}
        for key, val in query_dict.items():
            if isinstance(val, dict):
                new_query_dict[key] = self.range_min_max_to_target(val)
            else:
                new_query_dict[key] = val
        return new_query_dict

    def get_recommendation_parameters(self, prompt, debug=True):
        if debug:
            generated_json = """{"genres":["classical", "ambient"],
    "playlist_name": "[TEST] Starry Night Vibes",
    "energy": {"min": 0, "max": 0.3},
    "danceability": {"min": 0, "max": 0.3},
    "valence": {"min": 0.6, "max": 0.9},
    "acousticness": {"min": 0.7, "max": 1},
    "artists": ["Ludovico Einaudi", "Nujabes", "Gustavo Santaolalla", "Hans Zimmer"]
    }"""
        else:
            # Send the prompt to the OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300,
                n=1,
                stop=None,
                temperature=1.0,
            )
            # Extract the generated JSON from the response
            generated_json = beginning_of_json + response.choices[0].text.strip()
            print(generated_json)
        try:
            playlist_data = json.loads(generated_json)

            playlist_data["seed_genres"] = self.filter_genres(playlist_data["genres"])

            if "artists" in playlist_data:
                playlist_data["seed_artists"] = self.get_ids_from_search(
                    playlist_data["artists"], search_type="artist"
                )
                if len(playlist_data["seed_artists"]) > 1:
                    playlist_data["seed_genres"] = playlist_data["seed_genres"][:1]

            if "tracks" in playlist_data:
                playlist_data["seed_tracks"] = self.get_ids_from_search(
                    playlist_data["tracks"], search_type="track"
                )
                if len(playlist_data["seed_tracks"]) > 1:
                    playlist_data["seed_artists"] = playlist_data["seed_artists"][:1]

        except json.decoder.JSONDecodeError:
            print(generated_json)
            print("FAILED TO GENERATE VALID JSON")

        print()

        return playlist_data

    def get_playlist_query_with_ranges(self, spotify_search_dict: dict):
        new_search_dict = {}
        for k, v in spotify_search_dict.items():
            if isinstance(v, dict):
                for range_key, range_val in v.items():
                    new_search_dict[f"{range_key}_{k}"] = range_val
            else:
                new_search_dict[k] = spotify_search_dict[k]
        return new_search_dict

    def filter_genres(self, genre_names):
        remaining = []
        for genre in genre_names:
            if genre in recommendation_genres:
                remaining.append(genre)
        if not remaining:
            print(genre_names)
            raise ValueError("No genres returned!")
        return remaining

    def find_artist(self, artist_id):
        uri = f"spotify:artist:{artist_id}"
        return self.spotify_handler.spotify.artist(uri)

    def get_ids_from_search(self, names, search_type="artist"):
        """search_type can be artist or tracks currently"""
        print("getting artists ids")
        pieces = []
        for name in names:
            print(name)
            result = self.spotify_handler.spotify.search(
                name, type=search_type, limit=10
            )
            pieces.append(result[f"{search_type}s"]["items"][0]["id"])
        return pieces

    def get_track_recommendations(self, genres=[""], **kwargs):
        tracks = self.spotify_handler.spotify.recommendations(**kwargs)["tracks"]
        track_names = [
            f'{track["name"]} - {track["artists"][0]["name"]}' for track in tracks
        ]
        track_ids = [track["id"] for track in tracks]
        track_ids = list(set(track_ids))
        print("\n".join(track_names))
        return track_ids

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
        music_request=None,
        debug=False,
        num_tracks=20,
        num_enhanced_tracks_to_add=3,
    ):
        music_request = music_request or ""
        formatted_prompt = prompt.format(
            beginning_of_json=beginning_of_json, music_request=music_request
        )
        raw_playlist_query = self.get_recommendation_parameters(
            formatted_prompt, debug=debug
        )
        print("Got playlist parameters")
        range_playlist_query = self.get_playlist_query_with_ranges(raw_playlist_query)
        track_ids = self.get_track_recommendations(**range_playlist_query)
        print(len(track_ids))
        while len(track_ids) < num_tracks:
            print("Enhancing the playlist...")
            target_range_query = self.get_playlist_query_with_targets(
                raw_playlist_query
            )
            print(target_range_query)
            if track_ids:
                target_range_query = self.get_seed_tracks_query(
                    target_range_query, track_ids
                )
            print(target_range_query)
            new_track_ids = self.get_track_recommendations(**target_range_query)
            track_ids.extend(new_track_ids[:num_enhanced_tracks_to_add])
            track_ids = list(set(track_ids))
            print(len(track_ids))
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
        return raw_playlist_query, playlist_name