import logging
import time

import pytest
from click.testing import CliRunner
from click.testing import Result
from retry import retry
from ytmusic_deleter import common
from ytmusic_deleter.cli import cli
from ytmusic_deleter.duplicates import check_for_duplicates
from ytmusicapi import YTMusic
from ytmusicapi.models.content.enums import VideoType
from ytmusicapi.type_alias import JsonDict
from ytmusicapi.type_alias import JsonList


def test_configure_logging_adds_file_handler_when_other_handlers_exist(tmp_path):
    from ytmusic_deleter.cli import configure_logging

    logger = logging.getLogger()
    existing_handler = logging.NullHandler()
    logger.addHandler(existing_handler)

    original_handlers = list(logger.handlers)
    try:
        log_file_path = configure_logging(tmp_path, no_logfile=False, verbose=False)

        file_handlers = [
            handler
            for handler in logger.handlers
            if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(log_file_path)
        ]
        assert file_handlers
    finally:
        for handler in list(logger.handlers):
            if handler not in original_handlers:
                logger.removeHandler(handler)
                handler.close()
        logger.removeHandler(existing_handler)


class TestCli:
    @staticmethod
    def delete_add_all_playlists(yt_browser: YTMusic, source: str):
        title_prefix = f"New Playlist from {source} "
        playlists = yt_browser.get_library_playlists(limit=None)
        for playlist in playlists:
            if playlist.get("title", "").startswith(title_prefix):
                yt_browser.delete_playlist(playlist["playlistId"])

    @staticmethod
    def get_add_all_playlist(yt_browser: YTMusic, source: str, playlist_number: int = 1):
        playlist_title = f"New Playlist from {source} {playlist_number}"

        @retry(AssertionError, tries=5, delay=3.0)
        def _get_playlist():
            playlists = yt_browser.get_library_playlists(limit=None)
            playlist_id = next(
                (playlist["playlistId"] for playlist in playlists if playlist.get("title") == playlist_title),
                None,
            )
            assert playlist_id, f"Playlist {playlist_title!r} was not created"
            playlist = yt_browser.get_playlist(playlist_id, limit=None)
            assert playlist.get("tracks") is not None
            return playlist

        return _get_playlist()

    def test_delete_uploads(self, yt_browser: YTMusic, upload_song, cleanup_uploads):
        result = CliRunner().invoke(cli, ["delete-uploads"], standalone_mode=False, obj=yt_browser)
        print(result.stdout)
        assert result.exit_code == 0

        albums_deleted, albums_total = result.return_value
        assert albums_deleted >= 1, f"No uploads were deleted. {albums_total} uploads were found."
        uploads_remaining = yt_browser.get_library_upload_songs(limit=None)
        assert len(uploads_remaining) == 0

    def test_add_to_library(self, yt_browser: YTMusic, upload_song, config, cleanup_uploads, upload_file_path):
        result: Result = CliRunner().invoke(cli, ["delete-uploads", "-a"], standalone_mode=False, obj=yt_browser)
        print(result.stdout)
        assert result.exit_code == 0

        assert self.verify_added_to_library(yt_browser, config, result, upload_file_path)

    def verify_added_to_library(self, yt_browser: YTMusic, config, result: Result, upload_file_path):
        albums_deleted, albums_total = result.return_value
        assert albums_deleted >= 1, f"No uploads were deleted. {albums_total} uploads were found."
        uploads_remaining = yt_browser.get_library_upload_songs(limit=None)
        assert len(uploads_remaining) == 0

        library_songs = yt_browser.get_library_songs(limit=None)
        for song in library_songs:
            if song.get("title").lower() in upload_file_path.lower():
                return True
        raise AssertionError("Uploaded song was not added to library before deleting")

    def test_remove_library(
        self, yt_browser: YTMusic, add_library_album, add_library_song, add_podcast, add_episodes_for_later
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["remove-library"], standalone_mode=False, obj=yt_browser)
        assert result.exit_code == 0
        albums_deleted, albums_total = result.return_value

        # Verify at least one album was removed
        assert albums_deleted >= 1, f"No library albums were removed. {albums_total} albums were found."

        # Verify there are no songs remaining in the library
        @retry(AssertionError, tries=5, delay=3.0)
        def _verify_no_songs_remaining():
            songs_remaining = yt_browser.get_library_songs(limit=None)
            assert len(songs_remaining) == 0, f"Not all songs were removed. {len(songs_remaining)} still remain."

        _verify_no_songs_remaining()

        # Verify there are no podcasts remaining in the library
        # For some reason podcasts are taking longer to register that they've been deleted, so try it a few times
        retries_remaining = 5
        while retries_remaining:
            podcasts_remaining = yt_browser.get_library_podcasts(limit=None)
            podcasts_remaining = list(filter(lambda podcast: podcast["channel"]["id"], podcasts_remaining))
            if len(podcasts_remaining) == 0:
                break
            retries_remaining -= 1
            time.sleep(2)
        assert len(podcasts_remaining) == 0, f"Not all podcasts were removed. {len(podcasts_remaining)} still remain."

        # Verify "Episodes for Later" playlist is empty
        episodes_for_later_playlist: JsonDict | None = yt_browser.get_playlist(
            common.SAVED_EPISODES_PLAYLIST_ID, limit=None
        )
        assert episodes_for_later_playlist is not None, f"{common.EPISODES_FOR_LATER!r} playlist could not be found"
        playlist_episodes: JsonList = episodes_for_later_playlist.get("tracks", [])
        assert len(playlist_episodes) == 0, f"{common.EPISODES_FOR_LATER!r} playlist still had episodes in it."

    def test_unlike_all_songs(self, yt_browser: YTMusic, like_songs, cleanup_library):
        runner = CliRunner()
        result = runner.invoke(cli, ["unlike-all"], standalone_mode=False, obj=yt_browser)
        assert result.exit_code == 0
        songs_unliked, songs_total = result.return_value
        assert songs_unliked == len(
            like_songs
        ), f"{songs_unliked} songs were unliked but there were {songs_total} liked songs."

        @retry(AssertionError, tries=5, delay=3.0)
        def _verify_no_likes_remaining():
            likes_remaining = yt_browser.get_liked_songs(limit=None)["tracks"]
            assert len(likes_remaining) == 0, f"There were still {len(likes_remaining)} liked songs remaining"

        _verify_no_likes_remaining()

    def test_delete_history(self, yt_browser: YTMusic, add_history_items):
        runner = CliRunner()
        result = runner.invoke(cli, ["delete-history"], standalone_mode=False, obj=yt_browser)
        assert result.exit_code == 0

        items_deleted = result.return_value
        assert items_deleted >= add_history_items, "One or more history items were not deleted"
        with pytest.raises(Exception, match="None"):
            yt_browser.get_history()

    def test_delete_playlists(self, yt_browser: YTMusic, create_playlist_and_delete_after):
        runner = CliRunner()
        result = runner.invoke(cli, ["delete-playlists"], standalone_mode=False, obj=yt_browser)
        assert result.exit_code == 0

        playlists_deleted, playlists_total = result.return_value
        assert playlists_deleted >= 1, f"No playlists were deleted. {playlists_total} were found in total."

    def test_sort_playlist(self, yt_browser: YTMusic, create_playlist_and_delete_after):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["sort-playlist", "Test Playlist (to be deleted)"], standalone_mode=False, obj=yt_browser
        )
        assert result.exit_code == 0

    @pytest.mark.skip(reason="Not super necessary to test, takes a while, might exceed rate limit")
    def test_shuffle_playlist(self, yt_browser: YTMusic, create_playlist_and_delete_after):
        runner = CliRunner()
        result = runner.invoke(cli, ["sort-playlist", "-s", "Test Playlist"], standalone_mode=False, obj=yt_browser)
        assert result.exit_code == 0

    def test_delete_playlist_exact_duplicates(self, yt_browser: YTMusic, create_playlist_with_dupes):
        # We can only test deletion of exact dupes because anything else requires terminal interaction
        time.sleep(3)  # wait for playlist to be created
        playlist = yt_browser.get_playlist(create_playlist_with_dupes)
        assert 3 == len(
            check_for_duplicates(playlist, yt_browser)
        ), "Playlist to work on did not contain the right number of duplicates"
        runner = CliRunner()
        result = runner.invoke(
            cli, ["remove-duplicates", "--exact", "Test Dupes (to be deleted)"], standalone_mode=False, obj=yt_browser
        )
        assert result.exit_code == 0

        time.sleep(3)  # wait for tracks to have been deleted
        processed_playlist = yt_browser.get_playlist(create_playlist_with_dupes, limit=None)
        assert 2 == len(
            check_for_duplicates(processed_playlist, yt_browser)
        ), "Playlist contained wrong number of remaining duplicates"

    def test_add_all_library_songs_to_playlist(self, yt_browser: YTMusic, add_library_album, cleanup_library):
        self.delete_add_all_playlists(yt_browser, "Library")
        library_songs = yt_browser.get_library_songs(limit=None)
        num_library_songs_with_video_id = sum(bool(song.get("videoId")) for song in library_songs)
        try:
            result = CliRunner().invoke(
                cli,
                ["add-all-to-playlist", "--library"],
                standalone_mode=False,
                obj=yt_browser,
            )
            assert result.exit_code == 0

            playlist = self.get_add_all_playlist(yt_browser, "Library")
            assert len(playlist.get("tracks", [])) == num_library_songs_with_video_id
        finally:
            self.delete_add_all_playlists(yt_browser, "Library")

    def test_add_all_uploaded_songs_to_playlist(self, yt_browser: YTMusic, upload_song, cleanup_uploads):
        self.delete_add_all_playlists(yt_browser, "Uploads")
        uploaded_songs = yt_browser.get_library_upload_songs(limit=None)
        num_uploaded_songs_with_video_id = sum(bool(song.get("videoId")) for song in uploaded_songs)
        try:
            result = CliRunner().invoke(
                cli,
                ["add-all-to-playlist", "--uploads"],
                standalone_mode=False,
                obj=yt_browser,
            )
            assert result.exit_code == 0

            playlist = self.get_add_all_playlist(yt_browser, "Uploads")
            assert len(playlist.get("tracks", [])) == num_uploaded_songs_with_video_id
        finally:
            self.delete_add_all_playlists(yt_browser, "Uploads")

    def test_add_all_playlist_tracks_to_library_via_title(
        self, yt_browser: YTMusic, get_playlist_with_dupes, cleanup_library
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["add-all-to-library", "Test Dupes"], standalone_mode=False, obj=yt_browser)
        # Playlist has 10 unique tracks even though it has 13 tracks
        assert (
            len(yt_browser.get_library_songs(limit=None)) == 10
        ), "Number of songs in library did not match number of songs in playlist"
        assert result.exit_code == 0

    def test_add_all_playlist_tracks_to_library_via_id(
        self, yt_browser: YTMusic, sample_public_playlist, cleanup_library
    ):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["add-all-to-library", sample_public_playlist], standalone_mode=False, obj=yt_browser
        )
        playlist_tracks = yt_browser.get_playlist(sample_public_playlist, limit=None)["tracks"]
        num_non_video_tracks = sum(track["videoType"] == VideoType.ATV for track in playlist_tracks)
        time.sleep(3)
        assert (
            len(yt_browser.get_library_songs(limit=None)) == num_non_video_tracks
        ), "Number of songs in library did not match number of songs in playlist"
        assert result.exit_code == 0

    def test_browser_auth(self, yt_browser: YTMusic):
        runner = CliRunner()
        result = runner.invoke(cli, ["whoami"], obj=yt_browser)
        assert result.exit_code == 0
        assert yt_browser is not None
        assert isinstance(yt_browser, YTMusic)

    @pytest.mark.xfail(reason="Google broke OAuth again: https://github.com/sigma67/ytmusicapi/issues/813")
    def test_oauth(self, yt_oauth):
        runner = CliRunner()
        result = runner.invoke(cli, ["whoami"], obj=yt_oauth)
        assert result.exit_code == 0
        assert yt_oauth is not None
        assert isinstance(yt_oauth, YTMusic)
        assert yt_oauth.get_account_info().get("accountName") == "Testy McTesterson"
