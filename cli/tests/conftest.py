import configparser
from pathlib import Path
from typing import Dict

import pytest
import time
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


@pytest.fixture(name="sample_video")
def fixture_sample_video() -> str:
    """Oasis - Wonderwall"""
    return "hpSrLjc5SMs"


@pytest.fixture(name="sample_playlist")
def fixture_sample_playlist() -> str:
    """very large playlist"""
    return "PL6bPxvf5dW5clc3y9wAoslzqUrmkZ5c-u"


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
        songs = yt_browser.get_library_upload_songs(limit=None)
        for song in songs:
            if song.get("title") in config["uploads"]["file"]:
                return song
        retries_remaining -= 1
