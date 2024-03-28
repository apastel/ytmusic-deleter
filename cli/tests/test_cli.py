from click.testing import CliRunner
from cli import cli
from ytmusicapi import YTMusic
import time


class TestCli:
    def test_delete_uploads(self, yt_browser: YTMusic, upload_song):
        assert upload_song
        result = CliRunner().invoke(cli, ["delete-uploads"], standalone_mode=False, obj=yt_browser)
        print(result.stdout)
        assert result.exit_code == 0
        albums_deleted, albums_total = result.return_value
        assert albums_deleted >= 1, f"No uploads were deleted. {albums_total} uploads were found."
        uploads_remaining = yt_browser.get_library_upload_songs(limit=None)
        assert len(uploads_remaining) == 0

    def test_remove_library(self, yt_oauth: YTMusic, add_library_album):
        assert add_library_album
        runner = CliRunner()
        result = runner.invoke(cli, ["remove-library"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0
        albums_deleted, albums_total = result.return_value
        assert albums_deleted >= 1, f"No library albums were removed. {albums_total} albums were found."
        songs_remaining = yt_oauth.get_library_songs(limit=None)
        assert len(songs_remaining) == 0

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
