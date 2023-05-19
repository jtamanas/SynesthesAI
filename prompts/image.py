from .shared_elements import (
    beginning_of_yaml,
    audio_features,
    instructions,
)

prompt = """{audio_features}

I have an image that I'll describe as `{{music_request}}`. I want a spotify playlist inspired by that image. The description has some names in it, but don't get confused, those are just the names of famous people and visual artists to help illuminate the style of the image.

{instructions} Again, none of the artists in the description are musical artists.

{beginning_of_yaml}""".format(
    beginning_of_yaml=beginning_of_yaml,
    audio_features=audio_features,
    instructions=instructions,
)
