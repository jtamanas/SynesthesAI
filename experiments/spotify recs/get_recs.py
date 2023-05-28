import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from examples import examples


def pretty_print_dict(dictionary, indent=0):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            print("\t" * indent + str(key) + ":")
            pretty_print_dict(value, indent + 1)
        else:
            print("\t" * indent + str(key) + ": " + str(value))


def parse_recs(recs):
    results = []
    for rec in recs["tracks"]:
        results.append(
            {
                "id": rec["id"],
                "name": rec["name"],
                "artist": rec["artists"][0]["name"],
            }
        )
    return results


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

for example in examples:
    pretty_print_dict(example)
    print()
    recs = spotify.recommendations(limit=5, **example)
    for rec in parse_recs(recs):
        pretty_print_dict(rec)
        print()
