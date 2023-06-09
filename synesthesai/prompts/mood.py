from .shared_elements import (
    beginning_of_toml,
    audio_features,
    instructions,
)

prompt = """{audio_features}

My music mood/request: `{{music_request}}`. I want a spotify playlist to match it. 

{instructions} If I mention some songs, add UP TO 4 to a list under the "tracks" key as well -- but ONLY if I mention a song.

{beginning_of_toml}""".format(
    beginning_of_toml=beginning_of_toml,
    audio_features=audio_features,
    instructions=instructions,
)
