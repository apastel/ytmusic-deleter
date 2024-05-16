import time

import pytest
from click.testing import CliRunner
from ytmusic_deleter.cli import check_for_duplicates
from ytmusic_deleter.cli import cli
from ytmusicapi import YTMusic


class TestCli:
    def test_delete_uploads(self, yt_browser: YTMusic, upload_song):
        result = CliRunner().invoke(cli, ["delete-uploads"], standalone_mode=False, obj=yt_browser)
        print(result.stdout)
        assert result.exit_code == 0

        albums_deleted, albums_total = result.return_value
        assert albums_deleted >= 1, f"No uploads were deleted. {albums_total} uploads were found."
        uploads_remaining = yt_browser.get_library_upload_songs(limit=None)
        assert len(uploads_remaining) == 0

    def test_remove_library(self, yt_oauth: YTMusic, add_library_album, add_podcast):
        runner = CliRunner()
        result = runner.invoke(cli, ["remove-library"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0
        albums_deleted, albums_total = result.return_value

        # Verify at least one album was removed
        assert albums_deleted >= 1, f"No library albums were removed. {albums_total} albums were found."

        # Verify there are no songs remaining in the library
        songs_remaining = yt_oauth.get_library_songs(limit=None)
        assert len(songs_remaining) == 0, f"Not all songs were removed. {len(songs_remaining)} still remain."

        # Verify there are no podcasts remaining in the library
        # For some reason podcasts are taking longer to register that they've been deleted, so try it a few times
        retries_remaining = 5
        while retries_remaining:
            podcasts_remaining = yt_oauth.get_library_podcasts(limit=None)
            podcasts_remaining = list(filter(lambda podcast: podcast["channel"]["id"], podcasts_remaining))
            if len(podcasts_remaining) == 0:
                break
            retries_remaining -= 1
            time.sleep(2)
        assert len(podcasts_remaining) == 0, f"Not all podcasts were removed. {len(podcasts_remaining)} still remain."

    def test_unlike_all_songs(self, yt_oauth: YTMusic, like_song):
        assert like_song
        runner = CliRunner()
        result = runner.invoke(cli, ["unlike-all"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0
        songs_unliked, songs_total = result.return_value
        assert songs_unliked >= 1, f"No songs were unliked. {songs_total} liked songs were found in total."
        time.sleep(5)
        likes_remaining = yt_oauth.get_liked_songs(limit=None)["tracks"]
        assert len(likes_remaining) == 0, f"There were still {len(likes_remaining)} liked songs remaining"

    def test_delete_history(self, yt_oauth: YTMusic, add_history_items):
        runner = CliRunner()
        result = runner.invoke(cli, ["delete-history"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0

        items_deleted = result.return_value
        assert items_deleted >= 7, "One or more history items were not deleted"

    def test_delete_playlists(self, yt_oauth: YTMusic, create_playlist):
        runner = CliRunner()
        result = runner.invoke(cli, ["delete-playlists"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0

        playlists_deleted, playlists_total = result.return_value
        assert playlists_deleted >= 1, f"No playlists were deleted. {playlists_total} were found in total."

    def test_sort_playlist(self, yt_oauth: YTMusic, create_playlist_and_delete_after):
        pass
        runner = CliRunner()
        result = runner.invoke(cli, ["sort-playlist", "Test Playlist"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0

    @pytest.mark.skip(reason="Not super necessary to test, takes a while, might exceed rate limit")
    def test_shuffle_playlist(self, yt_oauth: YTMusic, create_playlist):
        runner = CliRunner()
        result = runner.invoke(cli, ["sort-playlist", "-s", "Test Playlist"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0

    def test_delete_playlist_duplicates(self, yt_oauth: YTMusic, playlist_with_dupes):
        assert (
            len(check_for_duplicates(playlist_with_dupes, yt_oauth)) > 0
        ), "Playlist to work on did not contain any duplicates"
        runner = CliRunner()
        result = runner.invoke(cli, ["remove-duplicates", "Test Playlist"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0

        playlist_without_dupes = yt_oauth.get_playlist(playlist_with_dupes, limit=None)["id"]
        assert len(check_for_duplicates(playlist_without_dupes, yt_oauth)) == 0, "Playlist still contained duplicates"

    def test_delete_all(
        self,
        yt_browser: YTMusic,
        upload_song,
        add_library_album,
        add_podcast,
        create_playlist,
        like_song,
        add_history_items,
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["delete-all"], standalone_mode=False, obj=yt_browser)
        print(result.stdout)
        assert result.exit_code == 0

        # Verify everything was deleted
        assert 0 == len(yt_browser.get_library_upload_songs())
        assert 0 == len(yt_browser.get_library_songs())
        assert 1 == len(yt_browser.get_library_podcasts())
        assert "Episodes you save for later" == yt_browser.get_library_podcasts()[0].get("channel").get("name")
        assert 1 == len(yt_browser.get_library_playlists())
        assert "Episodes you save for later" == yt_browser.get_library_playlists()[0].get("description")
        assert 0 == len(yt_browser.get_liked_songs()["tracks"])
        with pytest.raises(Exception, match="None"):
            yt_browser.get_history()
