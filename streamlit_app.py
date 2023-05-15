from image_handler import ImageHandler
from spotify_handler import SpotifyHandler
from playlist_generator import PlaylistGenerator
import streamlit as st
import prompts.mood
import prompts.image
from css import css
from utils import dict_to_string
import os


class App:
    def __init__(
        self,
        spotify_handler,
    ):
        self.spotify_handler = spotify_handler
        self.playlist_generator = PlaylistGenerator(spotify_handler=spotify_handler)

    def title(self):
        st.markdown(
            "# Synesthes<span style='color:#ff6319'>ai</span>", unsafe_allow_html=True
        )

    def display_welcome(self):
        # define welcome
        auth_url = self.spotify_handler.oauth.get_authorize_url()

        welcome_msg = """
        Upload a <span style='color:#4060c9'><b>picture</b></span> or write a really specific description of your <span style='color:#925878'><b>mood</b></span>. I'll pass that onto <a target="_blank" href="{url}" >Spotify</a>
        to build a playlist just for you.
        """.format(
            url=auth_url
        )

        link_html = 'Sign into <a target="_blank" href="{url}" >{msg}</a>.'.format(
            url=auth_url,
            msg="Spotify",
            unsafe_allow_html=True,
        )

        self.title()

        if not st.session_state["signed_in"]:
            st.markdown(welcome_msg, unsafe_allow_html=True)
            st.markdown(link_html, unsafe_allow_html=True)

    def run(self):
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

        # set scope and establish connection
        scopes = " ".join(
            [
                "playlist-read-private",
                "playlist-modify-public",
            ]
        )
        # authenticate with response stored in url

        if not self.spotify_handler.app_authenticated():
            self.display_welcome()

        # after auth, get user info
        # only display the following after login
        ### is there another way to do this? clunky to have everything in an if:

        if "music_request" not in st.session_state:
            st.session_state[
                "music_request"
            ] = "I'm DJing a really cool party in Manhattan. I need music that won't interrupt the conversation but will get people moving and bobbing their heads. I'll be laughed out of the building if I play anything on the Billboard top 100 so keep it underground."

        if st.session_state["signed_in"]:
            self.title()
            # sp = st.session_state["sp"]
            user = self.spotify_handler.spotify.current_user()
            # name = user["display_name"]
            username = user["id"]

            placeholder = st.empty()
            isclick = placeholder.button("delete this button")
            image_col, text_col = placeholder.columns(2)
            with image_col:
                st.markdown(
                    "Listen to your <span style='color:#4060c9'><b>picture</b></span>.",
                    unsafe_allow_html=True,
                )
                uploaded_image = st.file_uploader(
                    "Upload an image here.",
                    type=["png", "jpg", "jpeg"],
                    label_visibility="collapsed",
                )

            with text_col:
                st.markdown(
                    "Or hear your <span style='color:#925878'><b>mood</b></span>.",
                    unsafe_allow_html=True,
                )
                music_request = st.text_area(
                    "Type your mood here.",
                    st.session_state["music_request"],
                    height=350,
                    label_visibility="collapsed",
                )

            if isclick:
                placeholder.empty()
            if uploaded_image:
                prompt = prompts.image.prompt
                image_handler = ImageHandler(uploaded_image)
                with st.spinner("describing your image..."):
                    music_request = image_handler.describe()
            else:
                prompt = prompts.mood.prompt

            if music_request and music_request != st.session_state["music_request"]:
                if len(music_request) > 2:
                    with st.spinner("making your playlist..."):
                        (
                            playlist_data,
                            playlist_id,
                        ) = self.playlist_generator.generate_playlist(
                            username=username,
                            prompt=prompt,
                            music_request=music_request,
                            debug=False,
                        )

                        if uploaded_image:
                            self.playlist_generator.set_playlist_cover_image(
                                playlist_id, image_handler.image_b64
                            )

                        st.session_state["music_request"] = music_request
                        st.text(dict_to_string(playlist_data))


if __name__ == "__main__":
    spotify_handler = SpotifyHandler()
    app = App(spotify_handler)
    app.run()
