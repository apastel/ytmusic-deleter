from typing import Dict
from typing import List

from ytmusic_deleter.common import can_edit_playlist
from ytmusic_deleter.duplicates import check_for_duplicates
from ytmusic_deleter.duplicates import remove_exact_dupes
from ytmusicapi import YTMusic


class TestPlaylists:
    def test_check_for_duplicates(
        self, yt_browser: YTMusic, get_playlist_with_dupes, expected_dupe_groups: List[List[Dict]]
    ):
        playlist = yt_browser.get_playlist(get_playlist_with_dupes)
        duplicate_groups = check_for_duplicates(playlist, yt_browser)

        assert lists_of_dictlists_equal(expected_dupe_groups, duplicate_groups)

    def test_remove_exact_dupes(self, expected_dupe_groups: List[List[Dict]]):
        expected_unique_groups = [
            [
                {"artist": "Metallica", "setVideoId": "017208FAA85233F9", "title": "Battery", "videoId": "hqnaXzz72H4"},
                {"artist": "Metallica", "setVideoId": "56B44F6D10557CC6", "title": "Battery", "videoId": "vA1nlwTbCvg"},
                {"artist": "Metallica", "setVideoId": "12EFB3B1C57DE4E1", "title": "Battery", "videoId": "RvW4OQFA_UY"},
                {
                    "artist": "Metallica",
                    "title": "Battery (live)",
                    "videoId": "_SAGhYJLynk",
                },
                {
                    "artist": "Metallica",
                    "title": "Battery (Early June 1985 Demo)",
                    "videoId": "pAhzcQRMqKg",
                },
            ],
            [
                {
                    "artist": "Iron Maiden",
                    "title": "The Number of the Beast (1998 Remaster)",
                    "videoId": "9646W4JSyf8",
                },
                {
                    "artist": "Iron Maiden",
                    "title": "The Number of the Beast",
                    "videoId": "sYXz3vZvtL8",
                },
            ],
        ]

        unique_groups, tracks_to_delete = remove_exact_dupes(expected_dupe_groups)

        assert lists_of_dictlists_equal(expected_unique_groups, unique_groups)
        expected_tracks_to_delete = [
            {"artist": "Metallica", "setVideoId": "017208FAA85233F9", "title": "Battery", "videoId": "hqnaXzz72H4"},
            {"artist": "Metallica", "setVideoId": "56B44F6D10557CC6", "title": "Battery", "videoId": "vA1nlwTbCvg"},
            {
                "artist": "Iron Maiden",
                "title": "Fear of the Dark",
                "videoId": "NmQN635Rheo",
            },
        ]
        assert lists_of_dicts_equal(expected_tracks_to_delete, tracks_to_delete)

    def test_can_edit_playlist(
        self, yt_browser: YTMusic, create_playlist_and_delete_after: str, sample_public_playlist: str, sample_video: str
    ):
        owned_playlist = yt_browser.get_playlist(create_playlist_and_delete_after)
        assert can_edit_playlist(owned_playlist), f"Playlist should be editable: {owned_playlist}"

        someone_elses_playlist = yt_browser.get_playlist(sample_public_playlist)
        assert not can_edit_playlist(
            someone_elses_playlist
        ), f"Playlist should not be editable: {someone_elses_playlist}"


def lists_of_dictlists_equal(list1, list2):
    def list_of_dicts_to_set(list):
        return {dict_to_frozenset(d) for sublist in list for d in sublist}

    set1 = list_of_dicts_to_set(list1)
    set2 = list_of_dicts_to_set(list2)

    return set1 == set2


def lists_of_dicts_equal(list1, list2):
    set1 = {dict_to_frozenset(d) for d in list1}
    set2 = {dict_to_frozenset(d) for d in list2}
    return set1 == set2


def dict_to_frozenset(d):
    filtered_dict = {
        k: v for k, v in d.items() if k != "setVideoId" and k != "album" and k != "duration" and k != "thumbnail"
    }
    return frozenset(filtered_dict.items())
