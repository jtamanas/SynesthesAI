from available_genres import list_of_recommendation_genres
from .constants import beginning_of_json


audio_features = """For each of the attributes below (except mode), you MUST provide a min and max if you specify it. 
```
Audio Features (Format: variable_name (range)): 
1. acousticness (0-1): Confidence in the track being acoustic. Higher values indicate higher confidence.
2. danceability (0-1): Suitability for dancing.
3. energy (0-1): Intensity and activity measure.
4. instrumentalness (0-1): Predicts absence of vocals.
5. key (int): Track's key using Pitch Class notation.
6. liveness (0-1): Presence of an audience.
7. loudness (float): Overall loudness.
8. speechiness (0-1): Presence of spoken words.
9. tempo (int): Estimated tempo in BPM.
10. valence (0-1): Musical positiveness.
```"""

prompt = """Here are the audio features available in the spotify api: {audio_features}

My music mood/request: `{{music_request}}`. 

Using this information, I want you to make a JSON that contains appropriate values for the attributes listed. Not every attribute needs to be listed, just the ones that you think are important to specify. This JSON will be passed to spotify to make a playlist. Be sure to include a six word summary of my mood as the name of the playlist -- be sure to match the tone of my reply. The final JSON should look like `{{beginning_of_json}} [...], "playlist_name": ..., "energy": {{{{"min": ..., "max": ...}}}}, ...`

This is the list of genres available on spotify: {list_of_recommendation_genres}. Don't recommend genres outside of that list. Finally, feel free to suggest up to 4 artists as a list of names under the key "artists". If I mention some songs, add those to a list under the "tracks" key as well -- but ONLY if I mention a song.

{{beginning_of_json}}""".format(
    audio_features=audio_features,
    list_of_recommendation_genres=list_of_recommendation_genres,
)
