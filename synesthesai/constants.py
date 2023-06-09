DEFAULT_SEARCH_PARAMETERS = {
    "genres": [],
    "artists": [],
    "tracks": [],
    "acousticness": {"min": 0, "max": 1},
    "danceability": {"min": 0, "max": 1},
    "energy": {"min": 0, "max": 1},
    "instrumentalness": {"min": 0, "max": 1},
    "liveness": {"min": 0, "max": 1},
    "loudness": {"min": -60, "max": 0},
    "tempo": {"min": 40, "max": 250},
    "valence": {"min": 40, "max": 250},
    "popularity": {"min": 0, "max": 100},
    "year": {"min": 0, "max": 3000},
    "mode": {"min": 0, "max": 1},
    "key": {"min": 0, "max": 11},
}

recommendation_genres = [
    "acoustic",
    "afrobeat",
    "alt-rock",
    "alternative",
    "ambient",
    "anime",
    "black-metal",
    "bluegrass",
    "blues",
    "bossanova",
    "brazil",
    "breakbeat",
    "british",
    "cantopop",
    "chicago-house",
    "children",
    "chill",
    "classical",
    "club",
    "comedy",
    "country",
    "dance",
    "dancehall",
    "death-metal",
    "deep-house",
    "detroit-techno",
    "disco",
    "disney",
    "drum-and-bass",
    "dub",
    "dubstep",
    "edm",
    "electro",
    "electronic",
    "emo",
    "folk",
    "forro",
    "french",
    "funk",
    "garage",
    "german",
    "gospel",
    "goth",
    "grindcore",
    "groove",
    "grunge",
    "guitar",
    "happy",
    "hard-rock",
    "hardcore",
    "hardstyle",
    "heavy-metal",
    "hip-hop",
    "holidays",
    "honky-tonk",
    "house",
    "idm",
    "indian",
    "indie",
    "indie-pop",
    "industrial",
    "iranian",
    "j-dance",
    "j-idol",
    "j-pop",
    "j-rock",
    "jazz",
    "k-pop",
    "kids",
    "latin",
    "latino",
    "malay",
    "mandopop",
    "metal",
    "metal-misc",
    "metalcore",
    "minimal-techno",
    "movies",
    "mpb",
    "new-age",
    "new-release",
    "opera",
    "pagode",
    "party",
    "philippines-opm",
    "piano",
    "pop",
    "pop-film",
    "post-dubstep",
    "power-pop",
    "progressive-house",
    "psych-rock",
    "punk",
    "punk-rock",
    "r-n-b",
    "rainy-day",
    "reggae",
    "reggaeton",
    "road-trip",
    "rock",
    "rock-n-roll",
    "rockabilly",
    "romance",
    "sad",
    "salsa",
    "samba",
    "sertanejo",
    "show-tunes",
    "singer-songwriter",
    "ska",
    "sleep",
    "songwriter",
    "soul",
    "soundtracks",
    "spanish",
    "study",
    "summer",
    "swedish",
    "synth-pop",
    "tango",
    "techno",
    "trance",
    "trip-hop",
    "turkish",
    "work-out",
    "world-music",
]
list_of_recommendation_genres_str = """{genres}""".format(genres=recommendation_genres)

DEBUG_TOML = """
playlist_name = "[TEST] Starry Night Vibes"
[genres]
values = ["classical", "ambient"]

[energy]
min = 0
max = 0.3

[danceability]
min = 0
max = 0.3

[valence]
min = 0.6
max = 0.9

[acousticness]
min = 0.7
max = 1

[year]
min = 1988
max = 2002

[artists]
values = ["Ludovico - Einaudi", "Nujabes", "Gustavo Santaolalla", "Hans Zimmer"]

[tracks]
values = [
  "Someone You Loved by Lewis Capaldi",
  "When the Party's Over by Billie Eilish",
  "Love Me Now by John Legend"
]
[broken]
values = [
                """