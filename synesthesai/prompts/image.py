from .shared_elements import (
    beginning_of_toml,
    audio_features,
    instructions,
)

prompt = """{audio_features}

I have an image that I'll describe as `{{music_request}}`. I want a playlist that will immerse me in the feelings of that piece.

{instructions} 

{beginning_of_toml}""".format(
    beginning_of_toml=beginning_of_toml,
    audio_features=audio_features,
    instructions=instructions,
)
