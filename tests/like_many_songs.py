import time

import ytmusicapi
from retry import retry
from ytmusic_deleter.common import string_exists_in_dict
from ytmusicapi.models.content.enums import LikeStatus

PLAYLISTS = [
    "PLpxuOeEi0yCQtge9JUBOH--_yqg-jUm4h",
    "PLCi8sXGJ0hKbFVx_c2ECZloCS9grABakb",
    "PL_9VDNdrlb8qexQEo8Wv6lsDj9y47WaK4",
    "PL0GvsLQil0MmYC96KEs_7dTNsLm1PS6JX",
    "PL3oR83GGTZrexHTHtnQiMgK_PAYBQK8CW",
    "PLPvifG5wxDzu-bzqr5-3qmfBp9MUdmRak",
    "PLcirGkCPmbmFMTvVKFvcG_tRAPkN_QcV1",
    "PLDOKvyJ5DdJDVrjzZAt7GZse-CuPA5VNn",
    "PLVAReimCtbfNddu-Ukz62vgKXzAg9egjb",
    "PLtJCksbabIPyfutcI3Kx9mg6h87p2DXzE",
    "PLEXox2R2RxZKyTTlt3kxvtJbI_Cw1K1IX",
    "PLtJCksbabIPyfutcI3Kx9mg6h87p2DXzE",
    "PLEXox2R2RxZJPZVYvKAQ2CH6wfulo5RHS",
    "PLxxogMB1b7qOC-agget0nN363IFXYHaQe",
]


def like_many_songs(yt_browser: ytmusicapi.YTMusic, long_song_list):
    total_songs_to_like = len(long_song_list)

    @retry(AssertionError, tries=10, delay=1)
    def _like_song(song):
        response = yt_browser.rate_song(song, LikeStatus.LIKE)
        if not string_exists_in_dict(response, "consistencyTokenJar"):
            raise AssertionError("Did not find 'consistencyTokenJar' in response")
        if not string_exists_in_dict(response, "Saved to liked music"):
            raise AssertionError("Did not find 'Saved to liked music' in response")

    for idx, song in enumerate(long_song_list):
        print(f"liking song {idx + 1} out of {total_songs_to_like}")
        try:
            _like_song(song)
        except AssertionError:
            print("Skipping failing track...")

    time.sleep(5)
    liked_songs = yt_browser.get_liked_songs(limit=None)["tracks"]
    return liked_songs


yt_browser = ytmusicapi.YTMusic("./tests/resources/browser.json")

for playlist in PLAYLISTS:
    playlist_items = yt_browser.get_playlist(playlist, limit=None)
    song_list = {track["videoId"] for track in playlist_items["tracks"]}
    like_many_songs(yt_browser, song_list)
