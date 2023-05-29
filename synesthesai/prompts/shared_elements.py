from datetime import datetime
from constants import list_of_recommendation_genres_str

beginning_of_toml = 'playlist_name = "'

key_description = """This is a description of the 24 musical keys in western music:
0. C Minor: Dramatic, mournful, introspective.
1. C# Minor / D♭ Minor: Mysterious, somber, reflective.
2. D Minor: Brooding, melancholic, introspective.
3. E♭ Minor / D# Minor: Deeply sorrowful, dark, ominous.
4. E Minor: Introspective, mournful, anxious.
5. F Minor: Despairing, anxious, melancholic.
6. F# Minor / G♭ Minor: Sorrowful, mournful, somber.
7. G Minor: Serious, moody, despairing.
8. A♭ Minor / G# Minor: Dark, mysterious, foreboding.
9. A Minor: Introspective, contemplative, melancholic.
10. B♭ Minor / A# Minor: Deeply sorrowful, brooding, despairing.
11. B Minor: Sombre, introspective, mournful.
12. C Major: Bright, happy, pure.
13. C# Major / D♭ Major: Warm, smooth, confident.
14. D Major: Joyful, triumphal, lively.
15. E♭ Major / D# Major: Warm, powerful, resolute.
16. E Major: Majestic, vibrant, confident.
17. F Major: Calm, warm, soothing.
18. F# Major / G♭ Major: Triumphal, bold, victorious.
19. G Major: Cheerful, playful, sunny.
20. A♭ Major / G# Major: Majestic, powerful, introspective.
21. A Major: Optimistic, joyful, cheerful.
22. B♭ Major / A# Major: Warm, relaxing, comforting.
23. B Major: Bright, energetic, joyous.

Please also include a list of all of the keys (by number) whose moods match the playlist you are curating. 
"""

audio_features = """Here are the audio features available in the spotify api -- for each of these features below, provide a min and max if you specify it:
```
Audio Features (Format: variable_name (range)): 
1. acousticness (0-1): Confidence in the track being acoustic. Higher values indicate higher confidence.
2. danceability (0-1): Suitability for dancing.
3. energy (0-1): Intensity and activity measure.
4. instrumentalness (0-1): Predicts absence of vocals. The closer to 1.0, the greater likelihood the track lacks vocal content.
5. key (int): Track's key using Pitch Class notation.
6. liveness (0-1): Presence of an audience.
7. loudness (float): Overall loudness.
8. tempo (int): Estimated tempo in BPM.
9. valence (0-1): Musical positiveness.
10. popularity (0-100): Current popularity. >70 is radio-worthy.
11. year (0-2023): Year of release. Be liberal in your ranges, unless specific periods are specified. It's currently {date}

{key_description}
```""".format(
    date=datetime.today().strftime("%B %Y"),
    key_description=key_description,
)


yaml_example = """```
{beginning_of_toml}The greatest playlist ever made"

[genres]
values = [...]

[keys]
values = [...]

[instrumentalness]
min = ...
max = ...

...
```""".format(
    beginning_of_toml=beginning_of_toml
)

instructions = """You're the world's best DJ. Using this information, I want you to make a TOML that contains appropriate values for the attributes listed. This TOML will be passed to spotify to make a playlist. Be sure to include a summary of my mood as the name of the playlist -- match the tone of my reply! The final TOML should look like:

{yaml_example}

This is the list of genres available on spotify: {list_of_recommendation_genres_str}. Every genre you recommend needs to come from that list. Pick at least one genre in this list and DO NOT recommend genres outside of the list. Finally, feel free to suggest up to 4 musical artists as a list of names under the key "artists".""".format(
    yaml_example=yaml_example,
    list_of_recommendation_genres_str=list_of_recommendation_genres_str,
)
