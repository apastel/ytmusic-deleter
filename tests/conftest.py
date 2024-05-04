import configparser
import time
from pathlib import Path
from typing import Dict

import pytest
from ytmusic_deleter import constants
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
    Return the song object or None if it did not upload successfully.
    """
    response = yt_browser.upload_song(get_resource(config["uploads"]["file"]))
    if not isinstance(response, str) and response.status_code == 409:
        # Song already uploaded
        return True

    assert response == "STATUS_SUCCEEDED" or response.status_code == 200

    # Wait for upload to finish processing
    retries_remaining = 10
    while retries_remaining:
        time.sleep(5)
        try:
            songs = yt_browser.get_library_upload_songs(limit=None)
        except KeyError:
            pass
        for song in songs:
            if song.get("title") in config["uploads"]["file"]:
                return song
        retries_remaining -= 1


@pytest.fixture(name="add_library_album")
def fixture_add_library_album(yt_oauth: YTMusic, sample_album_as_playlist):
    response = yt_oauth.rate_playlist(sample_album_as_playlist, constants.LIKE)
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


@pytest.fixture(name="add_podcast")
def fixtrue_add_podcast(yt_oauth: YTMusic, sample_podcast):
    response = yt_oauth.rate_playlist(sample_podcast, constants.LIKE)
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


@pytest.fixture(name="like_song")
def fixture_like_song(yt_oauth: YTMusic, sample_video):
    response = yt_oauth.rate_song(sample_video, constants.LIKE)
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
    yt_oauth.rate_playlist("OLAK5uy_lZ90LvUqQdKrByCbk99v54d8XpUOmFavo", constants.INDIFFERENT)


@pytest.fixture(name="create_playlist")
def fixture_playlist(yt_oauth: YTMusic, sample_public_playlist) -> str:
    playlist_id = yt_oauth.create_playlist("Test Playlist", "a test playlist", source_playlist=sample_public_playlist)

    return playlist_id


@pytest.fixture(name="playlist_with_dupes")
def fixture_playlist_with_dupes(yt_oauth: YTMusic, create_playlist):
    playlist_id = create_playlist
    playlist = yt_oauth.get_playlist(playlist_id)
    sample_video_id = playlist.get("tracks")[0].get("videoId")
    items_to_add = [sample_video_id]
    yt_oauth.add_playlist_items(playlist_id, items_to_add, duplicates=True)

    yield playlist_id

    yt_oauth.delete_playlist(playlist_id)
