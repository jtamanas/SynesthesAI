# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 19:35:20 2022

@author: jtamanas 

but huge shoutout to @chorg for figuring out how to log into spotify https://github.com/chorgan182/PlaylistPreserver/blob/qry-param-method/playlist_preserver_app.py
"""

# setup

# libraries
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import os
import datetime as dt
import time
import random
from genre_prompt import beginning_of_json, prompt
import json
import openai
from available_genres import recommendation_genres
from css import css

# spotify connection set up


# base func definitions


def dict_to_string(d):
    """
    Converts a dictionary into a pretty string.

    Args:
        d (dict): A dictionary with string keys and values that are numbers or lists.

    Returns:
        str: A pretty string representation of the dictionary.
    """
    lines = []
    for key, value in d.items():
        if isinstance(value, list):
            value_str = "[" + ", ".join(str(v) for v in value) + "]"
        else:
            value_str = str(value)
        lines.append(f"{key}: {value_str}")
    return "\n".join(lines)


def get_token(oauth, code):
    token = oauth.get_access_token(code, as_dict=False, check_cache=False)
    # remove cached token saved in directory
    os.remove(".cache")

    # return the token
    return token


def sign_in(token):
    sp = spotipy.Spotify(auth=token)
    return sp


def get_correct_limit(stop, start):
    """
    All credit to https://github.com/irenechang1510 for this function idea.
    """

    # start at 50 and move backwards until correct timestamp is found
    # re run the API call until 'before' is greater than the stop timestamp
    limit = 50
    while limit > 0:
        obj = sp.current_user_recently_played(before=start, limit=limit)
        mark = int(obj["cursors"]["before"])

        # get the track played right after the stop timestamp
        if mark > stop:
            break
        # otherwise, decrease the limit by 1 and try again
        limit -= 1

    return limit


### in the end, this endpoint is simply broken
### cannot do anything until Spotify fixes it
def get_recents_all(since):
    # for some reason, you have to move backwards instead of forward
    # the after header seems pointless because it still starts at current time
    # but the next() method returns a results object with no 'next' dict element?

    now = int(time.mktime(dt.datetime.now().timetuple())) * 1000
    start = now

    tracks = []
    while start > since:
        results = sp.current_user_recently_played(before=start, limit=50)
        try:
            next_stop = int(results["cursors"]["before"])
        except:
            next_stop = since
        # eventually, the next stop will move past the desired since timestamp
        if next_stop < since:
            last_limit = get_correct_limit(since, start)
            if last_limit != 0:
                results = sp.current_user_recently_played(
                    before=start, limit=last_limit
                )
            else:
                break
        tracks.extend(results["items"])
        start = next_stop
    return tracks


def get_playlists_all(username):
    results = sp.user_playlists(username)
    playlists = results["items"]
    while results["next"]:
        results = sp.next(results)
        playlists.extend(results["items"])
    return playlists


def get_tracks_all(username, playlist_id):
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results["items"]
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])
    return tracks


# app func definitions


def app_get_token():
    try:
        token = get_token(st.session_state["oauth"], st.session_state["code"])
    except Exception as e:
        st.error("An error occurred during token retrieval!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["cached_token"] = token


def app_sign_in():
    try:
        sp = sign_in(st.session_state["cached_token"])
    except Exception as e:
        st.error("An error occurred during sign-in!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["signed_in"] = True
        app_display_welcome()
        st.success("Sign in success!")

    return sp


def app_display_welcome():
    # define welcome
    welcome_msg = """
    Write a really specific description of the kind of mood you're in. I'll use that information
    to build a playlist just for you with music that spotify thinks you'll like.
    """

    # define temporary note
    note_temp = """
    Example: 
    
    _"I'm DJing a really cool party in Manhattan. I need music that won't interrupt the conversation but will get people moving and bobbing their heads. I'll be laughed out of the building if I play anything on the Billboard top 100 so keep it underground."_
    """

    st.title("Synesthesai")

    if not st.session_state["signed_in"]:
        st.markdown(welcome_msg)
        # st.write(
        #     " ".join(
        #         [
        #             "No tokens found for this session. Please log in by",
        #             "clicking the link below.",
        #         ]
        #     )
        # )
        st.markdown(note_temp)
        st.markdown(link_html, unsafe_allow_html=True)


def range_min_max_to_target(min_max_dict):
    """Takes in a dictionary with min,max keys. Returns a dictionary with target keys where target=mean(min, max)"""
    return {"target": (min_max_dict["min"] + min_max_dict["max"]) / 2}


def get_playlist_query_with_targets(query_dict):
    """Assumes it gets {other:val, ..., min_key:, max_key:, min_key1:, max_key1:, ...}"""
    new_query_dict = {}
    for key, val in query_dict.items():
        if isinstance(val, dict):
            new_query_dict[key] = range_min_max_to_target(val)
        else:
            new_query_dict[key] = val
    return new_query_dict


def get_recommendation_parameters(sp, prompt, debug=True):
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

        playlist_data["seed_genres"] = filter_genres(playlist_data["genres"])

        if "artists" in playlist_data:
            playlist_data["seed_artists"] = get_artist_ids(sp, playlist_data["artists"])
            if len(playlist_data["seed_artists"]) > 1:
                playlist_data["seed_genres"] = playlist_data["seed_genres"][:1]

    except json.decoder.JSONDecodeError:
        print(generated_json)
        print("FAILED TO GENERATE VALID JSON")

    print()

    return playlist_data


def get_playlist_query_with_ranges(spotify_search_dict: dict):
    new_search_dict = {}
    for k, v in spotify_search_dict.items():
        if isinstance(v, dict):
            for range_key, range_val in v.items():
                new_search_dict[f"{range_key}_{k}"] = range_val
        else:
            new_search_dict[k] = spotify_search_dict[k]
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


def find_artist(sp, artist_id):
    uri = f"spotify:artist:{artist_id}"
    return sp.artist(uri)


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


def get_track_recommendations(sp, genres=[""], **kwargs):
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


def get_track_uris(track_ids):
    return [f"spotify:track:{track_id}" for track_id in track_ids]


def create_spotify_playlist(sp, track_ids, playlist_name="Test", music_request=""):
    # Create a new playlist
    playlist = sp.user_playlist_create(
        SPOTIPY_USERNAME,
        playlist_name,
        public=True,
        description=music_request,
    )
    playlist_url = playlist["external_urls"]["spotify"]
    playlist_url = '<a target="_blank" href="{url}" >Now on Spotify: {msg}</a>'.format(
        url=playlist_url, msg=playlist_name
    )

    st.markdown(playlist_url, unsafe_allow_html=True)
    playlist_id = playlist["id"]

    # Add tracks to the playlist
    track_uris = get_track_uris(track_ids)
    print(track_uris)
    sp.playlist_add_items(playlist_id, track_uris)
    print(f"Playlist '{playlist_name}' created and tracks added successfully!")
    return playlist_id


def get_seed_tracks_query(playlist_data, track_ids, n=5):
    """This function takes in a list of tracks, chooses n(<=5) random ones, then uses those to get recs from spotify"""
    random_tracks = random.sample(track_ids, min(n, len(track_ids)))

    # clear out old search parameters so we don't get an error in our query
    for key in ["seed_genres", "seed_artists", "seed_tracks"]:
        if key in playlist_data:
            playlist_data.pop(key)

    playlist_data["seed_tracks"] = [track for track in random_tracks]
    return playlist_data


def generate_playlist(
    music_request=None, debug=False, num_tracks=20, num_enhanced_tracks_to_add=3
):
    """
    num_enhanced_tracks_to_add: is small because searching by target is often not very precise.
    But if we take the top k searches from a targetted search and then use those, it's possible
    that the resulting recommendations are more similar to the targets, than if we were to
    just search by target alone.
        This is because there are hidden attributes that are not available as targets for us,
        but that could be correlated amongst the top k.

        Not a good explanation, but it makes sense I swear.
    """
    music_request = music_request or ""

    formatted_prompt = prompt.format(
        beginning_of_json=beginning_of_json, music_request=music_request
    )
    raw_playlist_query = get_recommendation_parameters(
        sp, formatted_prompt, debug=debug
    )
    print("Got playlist parameters")
    range_playlist_query = get_playlist_query_with_ranges(raw_playlist_query)
    track_ids = get_track_recommendations(sp, **range_playlist_query)
    print(len(track_ids))
    while len(track_ids) < num_tracks:
        print("Enhancing the playlist...")
        # The previous search was too narrow so we relax the constraints
        target_range_query = get_playlist_query_with_targets(raw_playlist_query)
        print(target_range_query)
        if track_ids:
            target_range_query = get_seed_tracks_query(target_range_query, track_ids)
        print(target_range_query)

        new_track_ids = get_track_recommendations(sp, **target_range_query)
        track_ids.extend(new_track_ids[:num_enhanced_tracks_to_add])
        print(len(track_ids))
    print("Got track ids")

    if "playlist_name" in raw_playlist_query:
        playlist_name = raw_playlist_query["playlist_name"]
    else:
        playlist_name = "For your mood"

    playlist_id = create_spotify_playlist(
        sp, track_ids, playlist_name=playlist_name, music_request=music_request
    )
    print("Made the playlist")
    st.balloons()

    # sp.start_playback(playlist_id)
    # add_tracks_to_queue(sp, track_ids)
    return raw_playlist_query, playlist_name


# setup the page
# Add some styling with CSS selectors
st.markdown(css, unsafe_allow_html=True)

# app session variable initialization
if "signed_in" not in st.session_state:
    st.session_state["signed_in"] = False
if "cached_token" not in st.session_state:
    st.session_state["cached_token"] = ""
if "code" not in st.session_state:
    st.session_state["code"] = ""


# import secrets from streamlit deployment
cid = st.secrets["SPOTIPY_CLIENT_ID"]
csecret = st.secrets["SPOTIPY_CLIENT_SECRET"]
uri = st.secrets["SPOTIPY_REDIRECT_URI"]

# set scope and establish connection
scopes = " ".join(
    [
        "user-read-private",
        "playlist-read-private",
        "playlist-modify-private",
        "playlist-modify-public",
        "user-read-recently-played",
    ]
)

# create oauth object
oauth = SpotifyOAuth(
    scope=scopes, redirect_uri=uri, client_id=cid, client_secret=csecret
)
# store oauth in session
st.session_state["oauth"] = oauth

# retrieve auth url
auth_url = oauth.get_authorize_url()

link_html = '<a target="_blank" href="{url}" >{msg}</a>'.format(
    url=auth_url,
    msg="Sign into Spotify.",
    unsafe_allow_html=True,
)

if "oauth" not in st.session_state:
    # st.session_state["oauth"] = None
    st.session_state["oauth"] = oauth
    print("WE RESET THE OAUTH SESSION STATE")

# authenticate with response stored in url

# get current url (stored as dict)
url_params = st.experimental_get_query_params()

# attempt sign in with cached token
if st.session_state["cached_token"] != "":
    sp = app_sign_in()
# if no token, but code in url, get code, parse token, and sign in
elif "code" in url_params and st.session_state["oauth"] is not None:
    # all params stored as lists, see doc for explanation
    st.session_state["code"] = url_params["code"][0]
    app_get_token()
    sp = app_sign_in()
    st.session_state["sp"] = sp
# otherwise, prompt for redirect
else:
    app_display_welcome()

# after auth, get user info
# only display the following after login
### is there another way to do this? clunky to have everything in an if:

if "music_request" not in st.session_state:
    st.session_state["music_request"] = "I want to listen to Van Gogh’s starry night"

if st.session_state["signed_in"]:
    sp = st.session_state["sp"]
    user = sp.current_user()
    name = user["display_name"]
    SPOTIPY_USERNAME = user["id"]

    music_request = st.text_area("", st.session_state["music_request"])

    if music_request and music_request != st.session_state["music_request"]:
        if len(music_request) > 2:
            st.text("Processing your request...")
            playlist_data, playlist_name = generate_playlist(
                music_request=music_request, debug=False
            )

            st.text(dict_to_string(playlist_data))
            # st.markdown("_Picture to Playlist coming soon..._")
            st.session_state["music_request"]
