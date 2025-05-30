import configparser
import time
from pathlib import Path
from random import shuffle
from typing import Dict
from typing import List

import click.testing
import pytest
from ytmusic_deleter import auth
from ytmusic_deleter import cli
from ytmusic_deleter import common
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


@pytest.fixture(name="sample_album_browse_id")
def fixture_sample_album_browse_id(yt_browser: YTMusic) -> str:
    """Eminem - The Marshall Mathers LP2"""
    return yt_browser.get_album_browse_id("OLAK5uy_m7SR1Tcnj6GBV0Nq1sZko2Wct11MUGrNE")


@pytest.fixture(name="sample_album_as_playlist")
def fixture_sample_album_as_playlist() -> str:
    """Metallica - Metallica (The Black Album)"""
    return "OLAK5uy_mcL5K5E9IHM5GPQ-8AyzPM7JgQMMn1uhs"


@pytest.fixture(name="sample_video")
def fixture_sample_video() -> str:
    """Oasis - Wonderwall"""
    return "hpSrLjc5SMs"


@pytest.fixture(name="medium_song_list")
def fixture_sample_song_list() -> List[str]:
    return ["hpSrLjc5SMs", "PIuAFrLeXfY", "9gi4WwQcPW8", "beX-9wW5rL0", "8ay_BkRuv-o", "HGorCGszxZU", "t2rsf8SiMJY"]


@pytest.fixture(name="long_playlist")
def fixture_sample_long_playlist() -> str:
    """Large Playlist, 1,546 songs"""
    return "PLxxogMB1b7qNaDocA9LJb9BYlk4KFZWuv"


@pytest.fixture(name="long_song_list")
def fixture_long_song_list(yt_browser: YTMusic, long_playlist: str) -> set[str]:
    playlist_items = yt_browser.get_playlist(long_playlist, limit=None)
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


@pytest.fixture(name="fuzzy_test_data")
def fixture_fuzzy_test_data() -> List[Dict]:
    return [
        {
            "upload_artist": "The Offspring",
            "upload_title": "The Offspring",
            "expected_artist": "The Offspring",
            "expected_title": "The Offspring",
        },
        {
            "upload_artist": "Metallica",
            "upload_title": "Metallica Through The Never: Music From The Motion Picture [Disc 2]",
            "expected_artist": "Metallica",
            "expected_title": "Metallica Through The Never (Music From The Motion Picture)",
        },
        {
            "upload_artist": "Newsted",
            "upload_title": "Heavy Metal Music",
            "expected_artist": None,
            "expected_title": None,
        },
        {
            "upload_artist": "Between The Buried & Me",
            "upload_title": "Colors Live",
            "expected_artist": "Between the Buried and Me",
            "expected_title": "Colors_Live",
        },
        {
            "upload_artist": "Billy Joel",
            "upload_title": " Greatest Hits, Vol. 3",
            "expected_artist": "Billy Joel",
            "expected_title": "Greatest Hits Vol. III",
        },
        {
            "upload_artist": "Eminem",
            "upload_title": "The Marshall Mathers LP 2",
            "expected_artist": "Eminem",
            "expected_title": "The Marshall Mathers LP2",
        },
        {
            "upload_artist": "Iron Maiden",
            "upload_title": "A Real Live One",
            "expected_artist": None,
            "expected_title": None,
        },
        {
            "upload_artist": "The Beatles",
            "upload_title": "Meet The Beatles!",
            "expected_artist": None,
            "expected_title": None,
        },
        {
            "upload_artist": "Todd Snider",
            "upload_title": "Last Songs For The Daily Planet",
            "expected_artist": "Todd Snider",
            "expected_title": "Songs for the Daily Planet",
        },
        {
            "upload_artist": "John Prine",
            "upload_title": "John Prine Live",
            "expected_artist": "John Prine",
            "expected_title": "John Prine (Live)",
        },
        {
            "upload_artist": "Nightwish",
            "upload_title": "Once Upon a Tour - Live In Buenos Aires",
            "expected_artist": None,
            "expected_title": None,
        },
        {
            "upload_artist": "Eminem",
            "upload_title": "Relapse: Refill [Disc 2]",
            "expected_artist": None,
            "expected_title": None,
        },
        {
            "upload_artist": "Megadeth",
            "upload_title": "Rust In Peace Live",
            "expected_artist": None,
            "expected_title": None,
        },
        {
            "upload_artist": "The Beatles",
            "upload_title": "The Beatles' Second Album",
            "expected_artist": None,
            "expected_title": None,
        },
    ]


@pytest.fixture(name="sample_public_playlist")
def fixture_sample_playlist() -> str:
    """'00s Metal"""
    return "RDCLAK5uy_kx0d2-VPr69KAkIQOTVFq04hCBsJE9LaI"


@pytest.fixture(name="sample_podcast")
def fixture_sample_podcast() -> str:
    """JRE Archive"""
    return "PLk1Sqn_f33KuU_aJDvMPPAy_SoxXTt_ub"


@pytest.fixture(name="client_id")
def fixture_client_id(config) -> str:
    return config["auth"]["client_id"]


@pytest.fixture(name="client_secret")
def fixture_client_secret(config) -> str:
    return config["auth"]["client_secret"]


@pytest.fixture(name="credential_dir")
def fixture_credential_dir(config) -> str:
    return get_resource(config["auth"]["credential_dir"])


@pytest.fixture(name="yt_browser")
def fixture_yt_browser(credential_dir) -> YTMusic:
    """a non-brand account that is able to create uploads"""
    return auth.do_auth(credential_dir, False)


@pytest.fixture(name="yt_oauth")
def fixture_yt_oauth(credential_dir, client_id, client_secret) -> YTMusic:
    return auth.do_auth(credential_dir, True, client_id, client_secret)


@pytest.fixture(name="upload_file_path")
def fixture_upload_file_path(config) -> str:
    return get_resource(config["uploads"]["file_path"])


@pytest.fixture(name="upload_song")
def fixture_upload_song(config, yt_browser: YTMusic, upload_file_path) -> Dict | None:
    """
    Upload a song and wait for it to finish processing.
    """
    upload_response = yt_browser.upload_song(upload_file_path)
    if not isinstance(upload_response, str) and upload_response.status_code == 409:
        # Song is already in uploads. Delete it and re-upload.
        # Although this app is not responsible for verifying that upload works properly,
        # we still want to verify that no errors happen if we try to delete a song right
        # after it was uploaded, since this was an issue previously https://github.com/sigma67/ytmusicapi/issues/578.
        songs = yt_browser.get_library_upload_songs()
        if songs:
            delete_response = None
            for song in songs:
                if song.get("title") in upload_file_path:
                    delete_response = yt_browser.delete_upload_entity(song["entityId"])
            assert delete_response == "STATUS_SUCCEEDED"
        # Need to wait for song to be fully deleted
        time.sleep(10)
        # Now re-upload
        upload_response = yt_browser.upload_song(upload_file_path)

    assert upload_response == "STATUS_SUCCEEDED" or upload_response.status_code == 200

    # Wait for upload to finish processing
    retries_remaining = 20
    while retries_remaining:
        time.sleep(5)
        songs = yt_browser.get_library_upload_songs(limit=None)
        for song in songs:
            if song.get("title") in upload_file_path:
                return song
        retries_remaining -= 1

    raise AssertionError("Failed to verify uploaded song exists in library.")


@pytest.fixture
def cleanup_uploads(yt_browser: YTMusic):
    yield
    click.testing.CliRunner().invoke(cli.cli, ["delete-uploads"], standalone_mode=False, obj=yt_browser)


@pytest.fixture
def cleanup_library(yt_browser: YTMusic):
    yield
    click.testing.CliRunner().invoke(cli.cli, ["remove-library"], standalone_mode=False, obj=yt_browser)


@pytest.fixture(name="add_library_album")
def fixture_add_library_album(yt_browser: YTMusic, sample_album_as_playlist):
    response = yt_browser.rate_playlist(sample_album_as_playlist, common.LIKE)
    assert "actions" in response

    # Wait for album to finish processing
    retries_remaining = 5
    while retries_remaining:
        albums = yt_browser.get_library_albums(limit=None)
        for album in albums:
            if album.get("title") == "Metallica":
                return album
        retries_remaining -= 1
        time.sleep(2)

    raise AssertionError("Failed to confirm that album was added to library")


@pytest.fixture(name="add_library_song")
def fixture_add_library_song(yt_browser: YTMusic, sample_album_browse_id):
    # Currently can't work due to `edit_song_library_status` not working
    catalog_album = yt_browser.get_album(sample_album_browse_id)
    add_token = catalog_album.get("tracks")[0]["feedbackTokens"]["add"]
    print(add_token)
    response = yt_browser.edit_song_library_status([add_token])
    print(response)
    assert "actions" in response

    # Wait for song to finish processing
    retries_remaining = 5
    while retries_remaining:
        songs = yt_browser.get_library_songs(limit=None)
        for song in songs:
            if song.get("title") == "Walk On Water (feat. Beyoncé)":
                return song
        retries_remaining -= 1
        time.sleep(2)

    raise AssertionError("Failed to confirm that song was added to library")


@pytest.fixture(name="add_podcast")
def fixture_add_podcast(yt_browser: YTMusic, sample_podcast):
    response = yt_browser.rate_playlist(sample_podcast, common.LIKE)
    assert "actions" in response

    # Wait for podcast to be in library
    retries_remaining = 5
    while retries_remaining:
        podcasts = yt_browser.get_library_podcasts(limit=None)
        for podcast in podcasts:
            if podcast.get("title") == "JRE Archive - Episodes #701 - 1000":
                return podcast
        retries_remaining -= 1
        time.sleep(2)

    raise AssertionError("Failed to confirm that podcast was added to library")


@pytest.fixture(name="like_song")
def fixture_like_song(yt_browser: YTMusic, sample_video):
    response = yt_browser.rate_song(sample_video, common.LIKE)
    assert "actions" in response

    # Wait for song to finish processing
    retries_remaining = 5
    song_processed = False
    while retries_remaining and not song_processed:
        liked_songs = yt_browser.get_liked_songs(limit=None)
        for song in liked_songs["tracks"]:
            if song.get("title") == "Wonderwall":
                yield song
                song_processed = True
                break
        retries_remaining -= 1
        time.sleep(2)

    # Remove song from library to clean up
    yt_browser.rate_playlist("OLAK5uy_lZ90LvUqQdKrByCbk99v54d8XpUOmFavo", common.INDIFFERENT)


@pytest.fixture(name="like_songs")
def fixture_like_songs(yt_browser: YTMusic, medium_song_list):
    for song in medium_song_list:
        num_retries = 300
        existing_likes = yt_browser.get_liked_songs(limit=None)["tracks"]
        if any(common.string_exists_in_dict(existing_like, song) for existing_like in existing_likes):
            print(f"Song {song!r} was already in likes...")
            continue
        response = yt_browser.rate_song(song, common.LIKE)
        while num_retries > 0 and (not common.string_exists_in_dict(response, "consistencyTokenJar")):
            response = yt_browser.rate_song(song, common.LIKE)
            num_retries -= 1
        if num_retries == 0:
            pytest.fail(f"Ran out of tries to add song {song!r} to likes.")
    time.sleep(5)
    liked_songs = yt_browser.get_liked_songs(limit=None)["tracks"]
    assert len(liked_songs) >= len(medium_song_list)
    return liked_songs


@pytest.fixture(name="like_many_songs")
def fixture_like_many_songs(yt_browser: YTMusic, long_song_list):
    for song in long_song_list:
        response = yt_browser.rate_song(song, common.LIKE)
        num_retries = 300
        while num_retries > 0 and (
            not common.string_exists_in_dict(response, "Removed from liked music")
            or not common.string_exists_in_dict(response, "consistencyTokenJar")
        ):
            response = yt_browser.rate_song(song, common.LIKE)
            num_retries -= 1


@pytest.fixture(name="create_playlist")
def fixture_create_playlist(yt_browser: YTMusic, sample_public_playlist) -> str:
    playlist_id = yt_browser.create_playlist("Test Playlist", "a test playlist", source_playlist=sample_public_playlist)
    assert isinstance(playlist_id, str)

    return playlist_id


@pytest.fixture(name="create_playlist_and_delete_after")
def fixture_create_playlist_and_delete_after(yt_browser: YTMusic, sample_public_playlist):
    playlist_id = yt_browser.create_playlist(
        "Test Playlist (to be deleted)", "a test playlist", source_playlist=sample_public_playlist
    )
    assert isinstance(playlist_id, str)

    yield playlist_id

    yt_browser.delete_playlist(playlist_id)


@pytest.fixture(name="create_playlist_with_dupes")
def fixture_create_playlist_with_dupes(yt_browser: YTMusic, sample_song_list_dupes):
    playlist_id = yt_browser.create_playlist("Test Dupes (to be deleted)", "a test playlist with duplicates")
    shuffle(sample_song_list_dupes)
    yt_browser.add_playlist_items(playlist_id, sample_song_list_dupes, duplicates=True)

    yield playlist_id

    yt_browser.delete_playlist(playlist_id)


@pytest.fixture(name="get_playlist_with_dupes")
def fixture_get_playlist_with_dupes(yt_browser: YTMusic, sample_song_list_dupes):
    """
    Useful during development when we don't want to keep creating/deleting
    playlists which causes Google to put us in time-out.
    """
    playlists = yt_browser.get_library_playlists()
    dupe_playlist = next((playlist for playlist in playlists if playlist.get("title") == "Test Dupes"), None)
    if dupe_playlist:
        # Delete all songs from playlist
        playlist_id = dupe_playlist.get("playlistId")
        playlist_items = yt_browser.get_playlist(playlist_id).get("tracks")
        response = yt_browser.remove_playlist_items(playlist_id, playlist_items)
        assert "STATUS_SUCCEEDED" == response
    else:
        playlist_id = yt_browser.create_playlist("Test Dupes", "a test playlist with duplicates")

    # Add songs to playlist
    shuffle(sample_song_list_dupes)
    yt_browser.add_playlist_items(playlist_id, sample_song_list_dupes, duplicates=True)
    time.sleep(1)  # fixes issue where playlist is shown to have 0 tracks in it
    return playlist_id


@pytest.fixture(name="add_history_items")
def fixture_add_history_items(yt_browser: YTMusic, medium_song_list):
    num_songs_added = 0
    for song in medium_song_list:
        song = yt_browser.get_song(song, yt_browser.get_signatureTimestamp())
        try:
            response = yt_browser.add_history_item(song)
            response.raise_for_status()
        except Exception as e:
            print(e)
            print("skipping a song that couldn't be added to history...")
            continue
        assert response.status_code == 204
        num_songs_added += 1
    return num_songs_added
