import configparser
import time
from pathlib import Path
from random import shuffle
from typing import Dict
from typing import List

import pytest
from ytmusic_deleter import common as const
from ytmusicapi import YTMusic


def get_resource(file: str) -> str:
    data_dir = Path(__file__).parent
    return data_dir.joinpath(file).as_posix()


def get_config() -> configparser.RawConfigParser:
    config = configparser.RawConfigParser()
    config.read(get_resource("resources/test.cfg"), "utf-8")
    return config


@pytest.fixture(name="config")
def fixture_config() -> configparser.RawConfigParser:
    return get_config()


@pytest.fixture(name="sample_album")
def fixture_sample_album() -> str:
    """Eminem - Revival"""
    return "MPREb_4pL8gzRtw1p"


@pytest.fixture(name="sample_album_as_playlist")
def fixture_sample_album_as_playlist() -> str:
    """Eminem - Revival"""
    return "OLAK5uy_nMr9h2VlS-2PULNz3M3XVXQj_P3C2bqaY"


@pytest.fixture(name="sample_video")
def fixture_sample_video() -> str:
    """Oasis - Wonderwall"""
    return "hpSrLjc5SMs"


@pytest.fixture(name="sample_song_list")
def fixture_sample_song_list() -> List[str]:
    return ["hpSrLjc5SMs", "PIuAFrLeXfY", "9gi4WwQcPW8", "beX-9wW5rL0", "8ay_BkRuv-o", "HGorCGszxZU", "t2rsf8SiMJY"]


@pytest.fixture(name="sample_long_playlist")
def fixture_sample_long_playlist() -> str:
    """The Millennial Mixtape"""
    return "RDCLAK5uy_mplKe9BIYCO3ZuNWSHZr48bm9DUDzbWnE"


@pytest.fixture(name="sample_long_song_list")
def fixture_sample_long_song_list(yt_oauth: YTMusic, sample_long_playlist: str) -> set[str]:
    playlist_items = yt_oauth.get_playlist(sample_long_playlist, limit=None)
    return {track["videoId"] for track in playlist_items["tracks"]}


@pytest.fixture(name="sample_song_list_dupes")
def fixture_sample_song_list_dupes() -> List[str]:
    return [
        "vA1nlwTbCvg",  # title: "Battery", album: "Master of Puppets"
        "vA1nlwTbCvg",  # title: "Battery", album: "Master of Puppets"
        "hqnaXzz72H4",  # title: "Battery", album: "Master of Puppets (Remastered Expanded Edition")
        "hqnaXzz72H4",  # title: "Battery", album: "Master of Puppets (Remastered Expanded Edition")
        "pAhzcQRMqKg",  # title: "Battery (Early June 1985 Demo)", album: "Master of Puppets (Remastered Expanded Edition)"
        "RvW4OQFA_UY",  # title: "Battery", album: "Master of Puppets (Remastered Deluxe Box Set)""
        "_SAGhYJLynk",  # title: "Battery (Live)", album: "Seattle 1989 (live)"
        "5Ygeh_P3ZlQ",  # title: "Battery", artist: "Machine Head"
        "b_ObqZtxuj0",  # title: "The Thing That Should Not Be", album: "Master of Puppets"
        "NmQN635Rheo",  # title: "Fear of the Dark"
        "NmQN635Rheo",  # title: "Fear of the Dark"
        "sYXz3vZvtL8",  # title: "The Number of the Beast"
        "9646W4JSyf8",  # title: "The Number of the Beast (1998 Remaster)"
    ]


@pytest.fixture(name="expected_dupe_groups")
def fixture_expected_dupe_groups() -> List[List[Dict]]:
    return [
        [
            {"artist": "Metallica", "setVideoId": "017208FAA85233F9", "title": "Battery", "videoId": "hqnaXzz72H4"},
            {"artist": "Metallica", "setVideoId": "52152B4946C2F73F", "title": "Battery", "videoId": "hqnaXzz72H4"},
            {"artist": "Metallica", "setVideoId": "56B44F6D10557CC6", "title": "Battery", "videoId": "vA1nlwTbCvg"},
            {"artist": "Metallica", "setVideoId": "289F4A46DF0A30D2", "title": "Battery", "videoId": "vA1nlwTbCvg"},
            {"artist": "Metallica", "setVideoId": "12EFB3B1C57DE4E1", "title": "Battery", "videoId": "RvW4OQFA_UY"},
            {
                "artist": "Metallica",
                "setVideoId": "532BB0B422FBC7EC",
                "title": "Battery (live)",
                "videoId": "_SAGhYJLynk",
            },
            {
                "artist": "Metallica",
                "setVideoId": "090796A75D153932",
                "title": "Battery (Early June 1985 Demo)",
                "videoId": "pAhzcQRMqKg",
            },
        ],
        [
            {
                "artist": "Iron Maiden",
                "setVideoId": "984C584B086AA6D2",
                "title": "The Number of the Beast (1998 Remaster)",
                "videoId": "9646W4JSyf8",
            },
            {
                "artist": "Iron Maiden",
                "setVideoId": "D0A0EF93DCE5742B",
                "title": "The Number of the Beast",
                "videoId": "sYXz3vZvtL8",
            },
        ],
        [
            {
                "artist": "Iron Maiden",
                "setVideoId": "F63CD4D04198B046",
                "title": "Fear of the Dark",
                "videoId": "NmQN635Rheo",
            },
            {
                "artist": "Iron Maiden",
                "setVideoId": "476B0DC25D7DEE8A",
                "title": "Fear of the Dark",
                "videoId": "NmQN635Rheo",
            },
        ],
    ]


@pytest.fixture(name="sample_public_playlist")
def fixture_sample_playlist() -> str:
    """'00s Metal"""
    return "RDCLAK5uy_kx0d2-VPr69KAkIQOTVFq04hCBsJE9LaI"


@pytest.fixture(name="sample_podcast")
def fixture_sample_podcast() -> str:
    """JRE Archive"""
    return "PLk1Sqn_f33KuU_aJDvMPPAy_SoxXTt_ub"


@pytest.fixture(name="browser_filepath")
def fixture_browser_filepath(config) -> str:
    return get_resource(config["auth"]["browser_file"])


@pytest.fixture(name="oauth_filepath")
def fixture_oauth_filepath(config) -> str:
    return get_resource(config["auth"]["oauth_file"])


@pytest.fixture(name="yt")
def fixture_yt() -> YTMusic:
    return YTMusic()


@pytest.fixture(name="yt_browser")
def fixture_yt_auth(browser_filepath) -> YTMusic:
    """a non-brand account that is able to create uploads"""
    return YTMusic(browser_filepath)


@pytest.fixture(name="yt_oauth")
def fixture_yt_oauth(oauth_filepath) -> YTMusic:
    return YTMusic(oauth_filepath)


@pytest.fixture(name="yt_brand")
def fixture_yt_brand(config) -> YTMusic:
    return YTMusic(config["auth"]["headers"], config["auth"]["brand_account"])


@pytest.fixture(name="yt_empty")
def fixture_yt_empty(config) -> YTMusic:
    return YTMusic(config["auth"]["headers_empty"], config["auth"]["brand_account_empty"])


@pytest.fixture(name="upload_song")
def fixture_upload_song(config, yt_browser: YTMusic) -> Dict | None:
    """
    Upload a song and wait for it to finish processing.
    """
    upload_response = yt_browser.upload_song(get_resource(config["uploads"]["file"]))
    if not isinstance(upload_response, str) and upload_response.status_code == 409:
        # Song is already in uploads. Delete it and re-upload.
        # Although this app is not responsible for verifying that upload works properly,
        # we still want to verify that no errors happen if we try to delete a song right
        # after it was uploaded, since this was an issue previously https://github.com/sigma67/ytmusicapi/issues/578.
        songs = yt_browser.get_library_upload_songs()
        if songs:
            delete_response = None
            for song in songs:
                if song.get("title") in config["uploads"]["file"]:
                    delete_response = yt_browser.delete_upload_entity(song["entityId"])
            assert delete_response == "STATUS_SUCCEEDED"
        # Need to wait for song to be fully deleted
        time.sleep(10)
        # Now re-upload
        upload_response = yt_browser.upload_song(get_resource(config["uploads"]["file"]))

    assert upload_response == "STATUS_SUCCEEDED" or upload_response.status_code == 200

    # Wait for upload to finish processing
    retries_remaining = 20
    while retries_remaining:
        time.sleep(5)
        songs = yt_browser.get_library_upload_songs(limit=None)
        for song in songs:
            if song.get("title") in config["uploads"]["file"]:
                return song
        retries_remaining -= 1

    raise AssertionError("Failed to verify uploaded song exists in library.")


@pytest.fixture(name="add_library_album")
def fixture_add_library_album(yt_oauth: YTMusic, sample_album_as_playlist):
    response = yt_oauth.rate_playlist(sample_album_as_playlist, const.LIKE)
    assert "actions" in response

    # Wait for album to finish processing
    retries_remaining = 5
    while retries_remaining:
        albums = yt_oauth.get_library_albums(limit=None)
        for album in albums:
            if album.get("title") == "Revival":
                return album
        retries_remaining -= 1
        time.sleep(2)

    raise AssertionError("Failed to confirm that album was added to library")


@pytest.fixture(name="add_podcast")
def fixture_add_podcast(yt_oauth: YTMusic, sample_podcast):
    response = yt_oauth.rate_playlist(sample_podcast, const.LIKE)
    assert "actions" in response

    # Wait for podcast to be in library
    retries_remaining = 5
    while retries_remaining:
        podcasts = yt_oauth.get_library_podcasts(limit=None)
        for podcast in podcasts:
            if podcast.get("title") == "JRE Archive - Episodes #701 - 1000":
                return podcast
        retries_remaining -= 1
        time.sleep(2)

    raise AssertionError("Failed to confirm that podcast was added to library")


@pytest.fixture(name="like_song")
def fixture_like_song(yt_oauth: YTMusic, sample_video):
    response = yt_oauth.rate_song(sample_video, const.LIKE)
    assert "actions" in response

    # Wait for song to finish processing
    retries_remaining = 5
    song_processed = False
    while retries_remaining and not song_processed:
        liked_songs = yt_oauth.get_liked_songs(limit=None)
        for song in liked_songs["tracks"]:
            if song.get("title") == "Wonderwall":
                yield song
                song_processed = True
                break
        retries_remaining -= 1
        time.sleep(2)

    # Remove song from library to clean up
    yt_oauth.rate_playlist("OLAK5uy_lZ90LvUqQdKrByCbk99v54d8XpUOmFavo", const.INDIFFERENT)


@pytest.fixture(name="create_playlist")
def fixture_create_playlist(yt_oauth: YTMusic, sample_public_playlist) -> str:
    playlist_id = yt_oauth.create_playlist("Test Playlist", "a test playlist", source_playlist=sample_public_playlist)
    assert isinstance(playlist_id, str)

    return playlist_id


@pytest.fixture(name="create_playlist_and_delete_after")
def fixture_create_playlist_and_delete_after(yt_oauth: YTMusic, sample_public_playlist):
    playlist_id = yt_oauth.create_playlist(
        "Test Playlist (to be deleted)", "a test playlist", source_playlist=sample_public_playlist
    )
    assert isinstance(playlist_id, str)

    yield playlist_id

    yt_oauth.delete_playlist(playlist_id)


@pytest.fixture(name="create_playlist_with_dupes")
def fixture_create_playlist_with_dupes(yt_oauth: YTMusic, sample_song_list_dupes):
    playlist_id = yt_oauth.create_playlist("Test Dupes (to be deleted)", "a test playlist with duplicates")
    shuffle(sample_song_list_dupes)
    yt_oauth.add_playlist_items(playlist_id, sample_song_list_dupes, duplicates=True)

    yield playlist_id

    yt_oauth.delete_playlist(playlist_id)


@pytest.fixture(name="get_playlist_with_dupes")
def fixture_get_playlist_with_dupes(yt_oauth: YTMusic, sample_song_list_dupes):
    """
    Useful during development when we don't want to keep creating/deleting
    playlists which causes Google to put us in time-out.
    """
    playlists = yt_oauth.get_library_playlists()
    dupe_playlist = next((playlist for playlist in playlists if playlist.get("title") == "Test Dupes"), None)
    if dupe_playlist:
        # Delete all songs from playlist
        playlist_id = dupe_playlist.get("playlistId")
        playlist_items = yt_oauth.get_playlist(playlist_id).get("tracks")
        response = yt_oauth.remove_playlist_items(playlist_id, playlist_items)
        assert "STATUS_SUCCEEDED" == response
    else:
        playlist_id = yt_oauth.create_playlist("Test Dupes", "a test playlist with duplicates")

    # Add songs to playlist
    shuffle(sample_song_list_dupes)
    yt_oauth.add_playlist_items(playlist_id, sample_song_list_dupes, duplicates=True)
    return playlist_id


@pytest.fixture(name="add_history_items")
def fixture_add_history_items(yt_oauth: YTMusic, sample_long_song_list):
    num_songs_added = 0
    print(f"total songs to be added to history: {len(sample_long_song_list)}")
    print(sample_long_song_list)
    for song in sample_long_song_list:
        song = yt_oauth.get_song(song, yt_oauth.get_signatureTimestamp())
        try:
            print(f"Adding {song['videoDetails']['title']!r} to history...")
            response = yt_oauth.add_history_item(song)
            response.raise_for_status()
        except Exception as e:
            print(e)
            print("skipping a song that couldn't be added to history...")
            continue
        assert response.status_code == 204
        print(f"Added {song['videoDetails']['title']!r} to history...")
        num_songs_added += 1
        print(f"total songs added to history so far: {num_songs_added}")
    print(f"{num_songs_added} were added to history successfully")
    return num_songs_added
