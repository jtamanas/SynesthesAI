import streamlit as st
from rec import generate_playlist
import requests


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


music_request = st.text_area(
    "\"I'm DJing a really cool party in Manhattan. I need music that won't interrupt the conversation but will get people moving and bobbing their heads.\""
)


AUTH_URL = "https://accounts.spotify.com/api/token"

# POST
auth_response = requests.post(
    AUTH_URL,
    {
        "grant_type": "client_credentials",
        "client_id": st.secrets["SPOTIPY_CLIENT_ID"],
        "client_secret": st.secrets["SPOTIPY_CLIENT_SECRET"],
    },
)

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data["access_token"]


url = "https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aR7qd6V"
headers = {"Authorization": "Bearer {token}".format(token=access_token)}


print(requests.get(url=url, headers=headers).json())


if music_request:
    if len(music_request) > 2:
        st.text("Processing your request...")
        playlist_data, playlist_name = generate_playlist(
            music_request=music_request, debug=True
        )

        st.text(dict_to_string(playlist_data))
