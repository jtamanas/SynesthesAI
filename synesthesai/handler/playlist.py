import streamlit as st
from constants import DEBUG_TOML
from prompts.shared_elements import beginning_of_toml
import random
from utils import (
    approximately_the_same_str,
    partial_load_toml,
)
import tomllib as toml
from LLM.openai import OpenAI
from LLM.palm import PaLM
from music.artist import Artist
from music.playlist import Playlist
from music.track import Track


class PlaylistHandler:
    def __init__(self, spotify_handler, LLM_type="PaLM"):
        if LLM_type == "PaLM":
            self.LLM = PaLM(model="models/text-bison-001")
        elif LLM_type == "OpenAI":
            self.LLM = OpenAI(model="text-davinci-003")
        self.spotify_handler = spotify_handler
        self.max_tokens = 350
        self.temperature = 1.0
        self.playlist = None

    def get_recommendation_parameters(self, prompt, debug=True):
        try:
            if debug:
                generated_toml = DEBUG_TOML
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
            print("THIS IS THE TOML IMMEDIATELY AFTER PARSING")

            self.playlist = Playlist(**playlist_data)
            self.add_ids_to_music()
            # I hate that I'm calling this here
            # self.playlist.limit_number_of_seeds()

        except Exception as e:
            print(f"Unexpected error in get_recommendation_parameters: {e}")
            raise

    def add_ids_to_music(self):
        # Get artist IDs
        if hasattr(self.playlist, "artists"):
            artists = self.get_ids_from_search(
                names=self.playlist.artists,
                years=self.playlist.year,
                search_type="artist",
            )
            self.playlist.seed_artists = artists

        # Get track IDs
        if hasattr(self.playlist, "tracks"):
            tracks = self.get_ids_from_search(
                names=self.playlist.tracks,
                years=self.playlist.year,
                search_type="track",
            )
            self.playlist.seed_tracks = tracks

    def get_ids_from_search(self, names, years, search_type="artist"):
        if search_type == "artist":
            music_object = Artist
        elif search_type == "track":
            music_object = Track
        else:
            raise ValueError("Search type not artist nor track")
        print(f"getting {search_type} ids")
        pieces = []
        for name in names:
            print(name)
            result = self.spotify_handler.spotify.search(
                f"{name} year:{years['min']}-{years['max']}", type=search_type, limit=1
            )
            if result[f"{search_type}s"]["items"]:
                print("GETTING ID RESULT")
                print(result)
                print()
                result = music_object(**result[f"{search_type}s"]["items"][0])
                print(f"Searched for {name}, found: {result.name}")
                if approximately_the_same_str(name, result.name):
                    print(f"Adding {result.name} to results")
                    # Update this line to create a Track object
                    pieces.append(result)
        return pieces

    def get_track_recommendations(self, genres=[""], limit=10, **kwargs):
        print(kwargs)

        # ensure the seed_tracks, seed_artists, seed_genres are list of strings (IDs), not list of Track objects
        for seed in ["seed_tracks", "seed_artists", "seed_genres"]:
            if seed in kwargs and kwargs[seed]:
                kwargs[seed] = [
                    item.id
                    if isinstance(item, Track) or isinstance(item, Artist)
                    else item
                    for item in kwargs[seed]
                ]

        raw_tracks = self.spotify_handler.spotify.recommendations(
            limit=limit, **kwargs
        )["tracks"]

        all_track_objects = [Track(**track) for track in raw_tracks]
        # filter by year, ensuring only relevant tracks are added
        filtered_track_objects = self.playlist.filter_tracks_by_category(
            all_track_objects,
            category_range=kwargs["year"],
        )
        return filtered_track_objects[-limit:]

    def add_tracks_to_queue(self, tracks):
        for track in tracks:
            self.spotify_handler.spotify.add_to_queue(f"spotify:track:{track.id}")
        print("Tracks added to the queue successfully!")

    def get_track_uris(self, tracks):
        return [f"spotify:track:{track.id}" for track in tracks]

    def create_spotify_playlist(
        self, username, tracks, playlist_name="Test", music_request=""
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
        track_uris = self.get_track_uris(tracks)
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

    def get_seed_tracks_query(self, playlist_data, tracks, n=3):
        track_ids = [track.id for track in tracks]
        random_track_ids = random.sample(track_ids, min(n, len(track_ids)))
        playlist_data["seed_tracks"] = [track for track in random_track_ids]
        return playlist_data

    def generate_playlist(
        self,
        username,
        prompt,
        music_request=None,
        debug=False,
        num_tracks=15,
        num_enhanced_tracks_to_add=2,
    ):
        music_request = music_request or ""
        formatted_prompt = prompt.format(
            beginning_of_toml=beginning_of_toml, music_request=music_request
        )
        self.get_recommendation_parameters(formatted_prompt, debug=debug)
        print("Got playlist parameters")
        playlist_query = self.playlist.generate_playlist_query_with_ranges()

        # even if there are enough songs in the filter, the vibe of the playlist
        # tends to wander. By limiting the number of tracks from the initial
        # query, we can limit the vibe to just the first n songs
        # start with one song unless seed track is specified.
        track_list = self.get_track_recommendations(limit=1, **playlist_query)
        print("Number of tracks: ", len(track_list))
        while len(track_list) < num_tracks:
            print("Enhancing the playlist...")
            if track_list:
                self.playlist.seed_tracks = track_list
                # playlist_query = self.get_seed_tracks_query(playlist_query, track_list)
            new_track_list = self.get_track_recommendations(
                limit=num_enhanced_tracks_to_add, **playlist_query
            )
            unique_new_tracks = [
                track
                for track in new_track_list
                if track.id not in [t.id for t in track_list]
            ]
            if not unique_new_tracks:
                # if there are no more songs in the fixed ranges, make them targets
                print("NO MORE TRACKS IN RANGE. SWITCHING TO TARGETS")
                playlist_query = self.playlist.generate_playlist_query_with_targets()
            track_list.extend(unique_new_tracks)
            print("Number of tracks: ", len(track_list))
        print("Got track ids")

        if "playlist_name" in self.playlist.generate_query():
            playlist_name = self.playlist.playlist_name
        else:
            playlist_name = "For your mood"

        # track_ids = [track.id for track in track_list]
        playlist_id = self.create_spotify_playlist(
            username,
            track_list,
            playlist_name=playlist_name,
            music_request=music_request,
        )
        print("Made the playlist")
        st.balloons()
        return self.playlist.generate_query(), playlist_id
