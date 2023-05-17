from available_genres import list_of_recommendation_genres
from .shared_elements import audio_features

prompt = """Here are the audio features available in the spotify api: {audio_features}

My music mood/request: `{{music_request}}`. 

Using this information, I want you to make a YAML that contains appropriate values for the attributes listed. Not every attribute needs to be listed, just the ones that you think are important to specify. This YAML will be passed to spotify to make a playlist. Be sure to include a six word summary of my mood as the name of the playlist -- be sure to match the tone of my reply. The final YAML should look like `{{beginning_of_yaml}}...\nplaylist_name:  ...\nenergy:\n  min: ...\n  max: ...\n...`

This is the list of genres available on spotify: {list_of_recommendation_genres}. Don't recommend genres outside of that list. Finally, feel free to suggest up to 4 artists as a list of names under the key "artists". If I mention some songs, add those to a list under the "tracks" key as well -- but ONLY if I mention a song.

{{beginning_of_yaml}}""".format(
    audio_features=audio_features,
    list_of_recommendation_genres=list_of_recommendation_genres,
)
