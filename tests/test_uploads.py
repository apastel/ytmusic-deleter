import click.testing
import ytmusicapi
from ytmusic_deleter import uploads
from ytmusic_deleter.cli import cli


class TestUploads:
    def test_fuzzy_matching(self, yt_browser: ytmusicapi.YTMusic, fuzzy_test_data):
        self.yt_browser = yt_browser
        score_cutoff = 85
        num_correct = 0
        for group in fuzzy_test_data:
            upload_artist = group["upload_artist"]
            upload_title = group["upload_title"]
            match = uploads.add_album_to_library(upload_artist, upload_title, yt_browser, score_cutoff)
            if match is None:
                if group["expected_artist"] is None and group["expected_title"] is None:
                    print("Correctly failed to find match")
                    num_correct += 1
                else:
                    print("Failed to find any match when one was expected")
                    print(f"\tExpected: {group['expected_artist']} - {group['expected_title']}")
            elif not group["expected_artist"] and not group["expected_title"]:
                print("Found match when none was expected")
                print(f"\tFound: {match['artist']} - {match['title']}")
            elif (
                match["artist"].lower() == group["expected_artist"].lower()
                and match["title"].lower() == group["expected_title"].lower()
            ):
                print("Correctly found match")
                num_correct += 1
            else:
                print("Found incorrect match")
                print(f"\tExpected: {group['expected_artist']} - {group['expected_title']}")
                print(f"\tActual: {match['artist']} - {match['title']}")
        assert num_correct == len(fuzzy_test_data), f"Only {num_correct} out of {len(fuzzy_test_data)} were correct"

    def teardown_method(self, method):
        print(f"Cleaning up after {method.__name__}")
        click.testing.CliRunner().invoke(cli, ["remove-library"], standalone_mode=False, obj=self.yt_browser)
        print("Cleanup complete")
