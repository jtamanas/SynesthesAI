import openai
import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
from genre_prompt import beginning_of_json, prompt
import os
import logging
from available_genres import recommendation_genres
import streamlit as st


# Set your credentials here
SPOTIPY_CLIENT_ID = st.secrets["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = st.secrets["SPOTIPY_CLIENT_SECRET"]
SPOTIPY_USERNAME = st.secrets["SPOTIPY_USERNAME"]

# Authenticate with the OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]


logger = logging.getLogger()


def authenticate_spotify():
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri="http://localhost:8888/callback",
            scope="playlist-modify-public,app-remote-control,streaming,user-modify-playback-state",
            username=SPOTIPY_USERNAME,
        )
    )


def get_recommendation_parameters(sp, prompt, debug=True):
    if debug:
        generated_json = """{"genres":["trap", "dancehall", "rap", "hip-hop"],
 "energy": 0.68,
 "danceability": 0.8,
 "tempo": 150,
 "loudness": -8,
 "speechiness": 0.5}"""
    else:
        # Send the prompt to the OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=1.0,
        )
        # Extract the generated JSON from the response
        generated_json = beginning_of_json + response.choices[0].text.strip()
    try:
        playlist_data = json.loads(generated_json)

        playlist_data = fix_dict_keys(playlist_data)

        print(playlist_data)

        if "artists" in playlist_data:
            playlist_data["seed_artists"] = get_artist_ids(
                sp, playlist_data.pop("artists")
            )
            playlist_data.pop("seed_genres")

    except json.decoder.JSONDecodeError:
        print(generated_json)
        print("FAILED TO GENERATE VALID JSON")

    print()

    return playlist_data


def fix_dict_keys(spotify_search_dict: dict):
    new_search_dict = {}
    for k, v in spotify_search_dict.items():
        new_k = k
        if "artist" not in k and "genre" not in k:
            if isinstance(v, float) or isinstance(v, int):
                new_k = f"target_{k}"

        new_search_dict[new_k] = spotify_search_dict[k]
    new_search_dict["seed_genres"] = filter_genres(spotify_search_dict["genres"])
    return new_search_dict


def filter_genres(genre_names):
    remaining = []
    for genre in genre_names:
        if genre in recommendation_genres:
            remaining.append(genre)
    if not remaining:
        print(genre_names)
        raise ValueError("No genres returned!")
    return remaining


def get_artist_ids(sp, artist_names):
    print("getting artists ids")
    artists = []
    for artist_name in artist_names:
        print(artist_name)
        # there's some weirdness with the search. The limit=1
        # result is not the top result for some reason.
        # get top 10 and then only look at top 1
        result = sp.search(artist_name, type="artist", limit=10)
        artists.append(result["artists"]["items"][0]["id"])

    return artists


def get_track_recommendations(sp, **kwargs):
    tracks = sp.recommendations(**kwargs)["tracks"]
    track_names = [
        f'{track["name"]} - {track["artists"][0]["name"]}' for track in tracks
    ]
    track_ids = [track["id"] for track in tracks]
    print("\n".join(track_names))
    return track_ids


def add_tracks_to_queue(sp, track_ids):
    for track_id in track_ids:
        sp.add_to_queue(f"spotify:track:{track_id}")
    print("Tracks added to the queue successfully!")


def create_spotify_playlist(sp, track_ids, playlist_name="Test"):
    # Create a new playlist
    playlist = sp.user_playlist_create(
        SPOTIPY_USERNAME,
        playlist_name,
        public=True,
        description="Generated by OpenAI and Spotify APIs",
    )
    playlist_id = playlist["id"]

    # Add tracks to the playlist
    track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]
    sp.playlist_add_items(playlist_id, track_uris)
    print(f"Playlist '{playlist_name}' created and tracks added successfully!")
    return playlist_id


def generate_playlist(music_request=None, debug=False):
    music_request = music_request or ""
    playlist_name = "test"  # get_playlist_name(music_request)

    sp = authenticate_spotify()

    formatted_prompt = prompt.format(
        beginning_of_json=beginning_of_json, music_request=music_request
    )
    playlist_data = get_recommendation_parameters(sp, formatted_prompt, debug=debug)
    print("Got playlist parameters")
    track_ids = get_track_recommendations(sp, **playlist_data)
    print("Got track ids")
    playlist_id = create_spotify_playlist(sp, track_ids, playlist_name=playlist_name)
    print("Made the playlistMade the playlist")
    # sp.start_playback(playlist_id)
    # add_tracks_to_queue(sp, track_ids)
    return playlist_data, playlist_name


if __name__ == "__main__":
    music_request = input("What are you in the mood for?")
    generate_playlist(music_request=music_request, debug=True)
