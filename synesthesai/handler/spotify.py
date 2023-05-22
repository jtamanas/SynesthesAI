# libraries
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import os


class SpotifyHandler:
    def __init__(self):
        self.oauth = self.create_oauth()
        self.spotify = None
        st.session_state["oauth"] = self.oauth

    def create_oauth(self):
        scopes = " ".join(
            [
                "playlist-modify-public",
                "ugc-image-upload",
            ]
        )
        return SpotifyOAuth(
            scope=scopes,
            redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
            client_id=st.secrets["SPOTIPY_CLIENT_ID"],
            client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
        )

    def get_token(self, code):
        token = self.oauth.get_access_token(code, as_dict=False, check_cache=False)
        # remove cached token saved in directory
        os.remove(".cache")
        # return the token
        return token

    def sign_in(self, token):
        self.spotify = spotipy.Spotify(auth=token)
        print("SPOTIFY ACTIVATED")

    def app_authenticated(self):
        signed_in_successful = False
        url_params = st.experimental_get_query_params()
        # attempt sign in with cached token
        if st.session_state["cached_token"] != "":
            self.handle_app_sign_in()
            signed_in_successful = True
        # if no token, but code in url, get code, parse token, and sign in
        elif "code" in url_params and st.session_state["oauth"] is not None:
            # all params stored as lists, see doc for explanation
            st.session_state["code"] = url_params["code"][0]
            self.handle_app_token()
            self.handle_app_sign_in()
            st.session_state["sp"] = self.spotify
            signed_in_successful = True

        return signed_in_successful

    def handle_app_token(self):
        try:
            token = self.get_token(st.session_state["code"])
            st.session_state["cached_token"] = token
        except Exception as e:
            st.error("An error occurred during token retrieval!")
            st.write("The error is as follows:")
            st.write(e)

    def handle_app_sign_in(self):
        try:
            self.sign_in(st.session_state["cached_token"])
            st.session_state["signed_in"] = True
        except Exception as e:
            st.error("An error occurred during sign-in!")
            st.write("The error is as follows:")
            st.write(e)
