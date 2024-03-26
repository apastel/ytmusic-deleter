from click.testing import CliRunner
from cli import cli
from ytmusicapi import YTMusic


class TestCli:
    def test_delete_uploads(self, yt_browser: YTMusic, upload_song):
        assert upload_song
        result = CliRunner().invoke(cli, ["delete-uploads"], standalone_mode=False, obj=yt_browser)
        print(result.stdout)
        assert result.exit_code == 0
        albums_deleted, albums_total = result.return_value
        assert albums_deleted >= 1, f"No uploads were deleted. {albums_total} uploads were found."

    def test_remove_library(self, yt_oauth: YTMusic, add_library_album):
        assert add_library_album
        runner = CliRunner()
        result = runner.invoke(cli, ["remove-library"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0
        albums_deleted, albums_total = result.return_value
        assert albums_deleted >= 1, f"No library albums were removed. {albums_total} albums were found."

    def test_unlike_all_songs(self, yt_oauth):
        runner = CliRunner()
        result = runner.invoke(cli, ["unlike-all"], standalone_mode=False, obj=yt_oauth)
        print(result.stdout)
        assert result.exit_code == 0
        assert result.return_value == (0, 0)
