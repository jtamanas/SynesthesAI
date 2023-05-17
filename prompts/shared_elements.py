from datetime import datetime

audio_features = """For each of the attributes below, provide a min and max if you specify it. 
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
11. popularity (0-100): Current popularity. >70 is radio-worthy.
12. year (0-2023): Year of release. Be liberal in your ranges, unless specific periods are specified. It's currently {date}
12. mode (0-1): Major is represented by 1 and minor is 0.
```""".format(
    date=datetime.today().strftime("%B %Y")
)
