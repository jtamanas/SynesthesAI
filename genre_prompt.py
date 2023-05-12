from available_genres import list_of_recommendation_genres


beginning_of_json = """{"genres":"""

audio_features = """Formatted as: variable_name (range): description
```
1. acousticness (0-1): Confidence in the track being acoustic. Higher values indicate higher confidence.
2. danceability (0-1): Suitability for dancing based on tempo, rhythm stability, beat strength, and regularity.
3. energy (0-1): Intensity and activity measure based on dynamic range, perceived loudness, timbre, onset rate, and entropy.
4. instrumentalness (0-1): Predicts absence of vocals. Higher values indicate higher confidence in no vocal content.
5. key (int): Track's key using Pitch Class notation (0 = C, 1 = C♯/D♭, etc.). -1 if undetected.
6. liveness (0-1): Presence of an audience. Values above 0.8 indicate high probability of live performance.
7. loudness (float): Overall loudness averaged across the track, typically between -60 and 0 dB.
8. mode (0 or 1): Modality of the track. 1 for major, 0 for minor.
9. speechiness (0-1): Presence of spoken words. Higher values indicate more speech-like content.
10. tempo (dict(min=float, max=float)): Estimated tempo in beats per minute.
11. valence (0-1): Musical positiveness. Higher values indicate more positive-sounding tracks.
12. popularity (0-100): Integer representing popularity of a track is a value between 0 and 100, with 100 being the most popular.
```"""

prompt = """This is the list of genres available on spotify: {list_of_recommendation_genres}.

Additionally, here are the audio features available in the spotify api: {audio_features}

When asked about what I'm in the mood for, I replied "{{music_request}}". 

Using this information, I want you to make a JSON that contains appropriate values for the attributes listed. Not every attribute needs to be listed, just the ones that you think are important to specify. This JSON will be passed to spotify to make a playlist. Be sure to include an up-to-ten-word summary of my mood as the name of the playlist. The final JSON should look like `{{beginning_of_json}} [...], "playlist_name": ..., "energy": ...`, ...

{{beginning_of_json}}""".format(
    audio_features=audio_features,
    list_of_recommendation_genres=list_of_recommendation_genres,
)
