from .shared_elements import (
    beginning_of_toml,
    audio_features,
    instructions,
)

prompt = """{audio_features}

I have a piece of art that I'll describe as `{{music_request}}`. I want a playlist that will immerse me in the feelings of that piece. The description has some names in it, but don't get confused, those are just the names of famous people and visual artists to help illuminate the style of the image.

{instructions} Again, none of the artists in the description are musical artists.

{beginning_of_toml}""".format(
    beginning_of_toml=beginning_of_toml,
    audio_features=audio_features,
    instructions=instructions,
)
