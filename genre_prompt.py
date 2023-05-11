beginning_of_json = """{"genres":"""

audio_features = """
```
1. acousticness (0-1): Confidence in the track being acoustic. Higher values indicate higher confidence.
2. danceability (0-1): Suitability for dancing based on tempo, rhythm stability, beat strength, and regularity.
3. energy (0-1): Intensity and activity measure based on dynamic range, perceived loudness, timbre, onset rate, and entropy.
4. instrumentalness (0-1): Predicts absence of vocals. Higher values indicate higher confidence in no vocal content.
5. key (int): Track's key using Pitch Class notation (0 = C, 1 = C♯/D♭, etc.). -1 if undetected.
6. liveness (0-1): Presence of an audience. Values above 0.8 indicate high probability of live performance.
7. loudness (dB): Overall loudness averaged across the track, typically between -60 and 0 dB.
8. mode (0 or 1): Modality of the track. 1 for major, 0 for minor.
9. speechiness (0-1): Presence of spoken words. Higher values indicate more speech-like content.
10. tempo (dict(min=float, max=float)): Estimated tempo in beats per minute.
11. valence (0-1): Musical positiveness. Higher values indicate more positive-sounding tracks.
```"""


# output from spotipy.Spotify.recommendation_genre_seeds()
list_of_recommendation_genres = """['acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'anime', 'black-metal', 'bluegrass', 'blues', 'bossanova', 'brazil', 'breakbeat', 'british', 'cantopop', 'chicago-house', 'children', 'chill', 'classical', 'club', 'comedy', 'country', 'dance', 'dancehall', 'death-metal', 'deep-house', 'detroit-techno', 'disco', 'disney', 'drum-and-bass', 'dub', 'dubstep', 'edm', 'electro', 'electronic', 'emo', 'folk', 'forro', 'french', 'funk', 'garage', 'german', 'gospel', 'goth', 'grindcore', 'groove', 'grunge', 'guitar', 'happy', 'hard-rock', 'hardcore', 'hardstyle', 'heavy-metal', 'hip-hop', 'holidays', 'honky-tonk', 'house', 'idm', 'indian', 'indie', 'indie-pop', 'industrial', 'iranian', 'j-dance', 'j-idol', 'j-pop', 'j-rock', 'jazz', 'k-pop', 'kids', 'latin', 'latino', 'malay', 'mandopop', 'metal', 'metal-misc', 'metalcore', 'minimal-techno', 'movies', 'mpb', 'new-age', 'new-release', 'opera', 'pagode', 'party', 'philippines-opm', 'piano', 'pop', 'pop-film', 'post-dubstep', 'power-pop', 'progressive-house', 'psych-rock', 'punk', 'punk-rock', 'r-n-b', 'rainy-day', 'reggae', 'reggaeton', 'road-trip', 'rock', 'rock-n-roll', 'rockabilly', 'romance', 'sad', 'salsa', 'samba', 'sertanejo', 'show-tunes', 'singer-songwriter', 'ska', 'sleep', 'songwriter', 'soul', 'soundtracks', 'spanish', 'study', 'summer', 'swedish', 'synth-pop', 'tango', 'techno', 'trance', 'trip-hop', 'turkish', 'work-out', 'world-music']"""

prompt = """This is the list of genres available on spotify: {list_of_recommendation_genres}.

Additionally, here are the audio features available in the spotify api: {audio_features}

When asked about what I'm in the mood for, I replied "{{music_request}}". 

Using this information, I want you to make a JSON that contains appropriate values for the attributes listed. Not every attribute needs to be listed, just the ones that you think are important to specify. This JSON will be passed to spotify to make a playlist.

{{beginning_of_json}}""".format(
    audio_features=audio_features,
    list_of_recommendation_genres=list_of_recommendation_genres,
)
