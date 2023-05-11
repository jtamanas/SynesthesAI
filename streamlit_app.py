import streamlit as st
import pandas as pd
import numpy as np
from rec import generate_playlist
import streamlit as st

music_request = st.text_area(
    "Describe the mood or scene of your playlist.",
    "I'm DJing a really cool party in Manhattan. I need music that won't interrupt the conversation but will get people moving and bobbing their heads.",
)

generate_playlist(music_request=music_request, debug=True)
