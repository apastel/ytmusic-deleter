import unittest
from click.testing import CliRunner
import deleter


class TestDeleter(unittest.TestCase):
    def test_remove_albums_from_library(self):
        runner = CliRunner()
        result = runner.invoke(deleter.remove_albums_from_library)
        assert result.exit_code == 0

    def test_delete_uploads(self):
        runner = CliRunner()
        result = runner.invoke(deleter.delete_all_uploaded_albums('true'))
        assert result.exit_code == 0
