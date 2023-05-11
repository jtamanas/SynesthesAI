import streamlit as st
import pandas as pd
import numpy as np
from rec import generate_playlist
import streamlit as st


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

if music_request:
    if len(music_request) > 2:
        st.text("Processing your request...")
        playlist_data, playlist_name = generate_playlist(
            music_request=music_request, debug=False
        )

        st.text(dict_to_string(playlist_data))
