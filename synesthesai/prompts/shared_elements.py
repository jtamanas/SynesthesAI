from datetime import datetime
from constants import list_of_recommendation_genres_str

beginning_of_yaml = """genres:
  - """

audio_features = """Here are the audio features available in the spotify api -- for each of these features below, provide a min and max if you specify it:
```
Audio Features (Format: variable_name (range)): 
1. acousticness (0-1): Confidence in the track being acoustic. Higher values indicate higher confidence.
2. danceability (0-1): Suitability for dancing.
3. energy (0-1): Intensity and activity measure.
4. instrumentalness (0-1): Predicts absence of vocals.
5. key (int): Track's key using Pitch Class notation.
6. liveness (0-1): Presence of an audience.
7. loudness (float): Overall loudness.
8. speechiness (0-1): measure of the presence of spoken words, with values above 0.66 indicating tracks that are probably made entirely of spoken words, values between 0.33 and 0.66 indicating tracks that may contain both music and speech, and values below 0.33 indicating music and other non-speech-like tracks.
9. tempo (int): Estimated tempo in BPM.
10. valence (0-1): Musical positiveness.
11. popularity (0-100): Current popularity. >70 is radio-worthy.
12. year (0-2023): Year of release. Be liberal in your ranges, unless specific periods are specified. It's currently {date}
12. mode (0-1): Major is represented by 1 and minor is 0.
```""".format(
    date=datetime.today().strftime("%B %Y")
)


yaml_example = """```
{beginning_of_yaml}genre1
  - genre2
  ...
playlist_name:  ...
energy:
  min: ...
  max: ...
...
```""".format(
    beginning_of_yaml=beginning_of_yaml
)

instructions = """Using this information, I want you to make a YAML that contains appropriate values for the attributes listed. Not every attribute needs to be listed, just the ones that you think are important to specify. This YAML will be passed to spotify to make a playlist. Be sure to include a six word summary of my mood as the name of the playlist -- be sure to match the tone of my reply. The final YAML should look like:

{yaml_example}

This is the list of genres available on spotify: {list_of_recommendation_genres_str}. Pick at last one genre and don't recommend genres outside of that list. Finally, feel free to suggest up to 4 musical artists as a list of names under the key "artists".""".format(
    yaml_example=yaml_example,
    list_of_recommendation_genres_str=list_of_recommendation_genres_str,
)
