import unittest
from click.testing import CliRunner
import ytmusic_deleter.cli as cli


class TestCli(unittest.TestCase):
    def test_delete_uploads(self):
        runner = CliRunner()
        result = runner.invoke(cli.delete_uploads, ["--add-to-library"])
        assert result.exit_code == 0

    def test_remove_albums_from_library(self):
        runner = CliRunner()
        result = runner.invoke(cli.remove_library)
        assert result.exit_code == 0

    def test_unlike_all_songs(self):
        runner = CliRunner()
        result = runner.invoke(cli.unlike_all)
        assert result.exit_code == 0
