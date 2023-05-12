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


def create_spotify_playlist(sp, track_ids, playlist_name="Test", music_request=""):
    # Create a new playlist
    playlist = sp.user_playlist_create(
        SPOTIPY_USERNAME,
        playlist_name,
        public=True,
        description=music_request,
    )
    playlist_url = playlist["external_urls"]["spotify"]
    playlist_url = '<span style="color:green"><a target="_self" href="{url}" >{msg}</a></span>'.format(
        url=playlist_url, msg=playlist_name
    )

    st.markdown(playlist_url, unsafe_allow_html=True)
    playlist_id = playlist["id"]

    # Add tracks to the playlist
    track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]
    sp.playlist_add_items(playlist_id, track_uris)
    print(f"Playlist '{playlist_name}' created and tracks added successfully!")
    return playlist_id


def generate_playlist(music_request=None, debug=False):
    music_request = music_request or ""

    formatted_prompt = prompt.format(
        beginning_of_json=beginning_of_json, music_request=music_request
    )
    playlist_data = get_recommendation_parameters(sp, formatted_prompt, debug=debug)
    print("Got playlist parameters")
    track_ids = get_track_recommendations(sp, **playlist_data)
    print("Got track ids")

    if "playlist_name" in playlist_data:
        playlist_name = playlist_data["playlist_name"]
    else:
        playlist_name = "For your mood"

    playlist_id = create_spotify_playlist(
        sp, track_ids, playlist_name=playlist_name, music_request=music_request
    )
    print("Made the playlistMade the playlist")
    # sp.start_playback(playlist_id)
    # add_tracks_to_queue(sp, track_ids)
    return playlist_data, playlist_name


def app_remove_recent(username):
    nm_playlist = st.session_state["pl_selected"]
    since_date = st.session_state["since_date"]
    since_time = st.session_state["since_time"]
    nm_playlist_new = st.session_state["new_name"]
    shuffle = st.session_state["shuffle"]

    # get playlist id of selected playlist
    playlists = get_playlists_all(username)
    playlist_names = [x["name"] for x in playlists]
    playlist_ids = [x["id"] for x in playlists]
    pl_index = playlist_names.index(nm_playlist)
    pl_selected_id = playlist_ids[pl_index]

    # get playlist tracks of selected playlist
    pl_tracks = get_tracks_all(username, pl_selected_id)
    pl_ids = [x["track"]["id"] for x in pl_tracks]

    # get listening history
    # combine date inputs to datetime object
    since_combined = dt.datetime.combine(since_date, since_time)
    # needs to be in milliseconds
    since_unix = int(time.mktime(since_combined.timetuple())) * 1000
    recent_tracks = get_recents_all(since_unix)
    recent_ids = [x["track"]["id"] for x in recent_tracks]

    # create new playlist, info of playlist returned
    new_pl = sp.user_playlist_create(user=username, name=nm_playlist_new)
    # need to get id of new playlist
    new_pl_id = new_pl["id"]

    # remove recently played from selected playlist
    new_tracks = [x for x in pl_ids if x not in recent_ids]

    # shuffle if desired
    if shuffle:
        random.shuffle(new_tracks)

    # add tracks to new playlist!
    # can only write 100 at a time to the spotify API
    chunk_size = 100
    for i in range(0, len(new_tracks), chunk_size):
        chunk = new_tracks[i : i + chunk_size]
        sp.user_playlist_add_tracks(user=username, playlist_id=new_pl_id, tracks=chunk)

    # gotta do a celly
    st.success("New playlist created! Check your Spotify App")
    st.balloons()


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

# this SHOULD open the link in the same tab when Streamlit Cloud is updated
# via the "_self" target
link_html = (
    '<span style="color:green"><a target="_self" href="{url}" >{msg}</a></span>'.format(
        url=auth_url, msg="I'm ready. (Hold down and open in new tab on iphone)"
    )
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
if st.session_state["signed_in"]:
    sp = st.session_state["sp"]
    user = sp.current_user()
    name = user["display_name"]
    SPOTIPY_USERNAME = user["id"]

    music_request = st.text_area(
        "\"I want to listen to Van Gogh’s starry night .\""
    )

    if music_request:
        if len(music_request) > 2:
            st.text("Processing your request...")
            playlist_data, playlist_name = generate_playlist(
                music_request=music_request, debug=False
            )

            st.text(dict_to_string(playlist_data))
            # st.markdown("_Picture to Playlist coming soon..._")
