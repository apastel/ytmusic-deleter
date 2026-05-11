import logging

import pytest
from ytmusic_deleter.actions import ActionContext
from ytmusic_deleter.actions import delete_playlists
from ytmusic_deleter.actions import delete_history
from ytmusicapi.exceptions import YTMusicServerError
from ytmusicapi.models.content.enums import LikeStatus


def make_playlist(title, playlist_id):
    return {"title": title, "playlistId": playlist_id}


class FakePlaylistYTMusic:
    def __init__(self, playlists, delete_playlist_errors=None):
        self.playlists = playlists
        self.delete_playlist_errors = set(delete_playlist_errors or ())
        self.deleted_playlists = []
        self.rated_playlists = []
        self.loaded_playlists = []
        self.removed_playlist_items = []

    def get_library_playlists(self, limit=None):
        return self.playlists

    def delete_playlist(self, playlist_id):
        self.deleted_playlists.append(playlist_id)
        if playlist_id in self.delete_playlist_errors:
            raise YTMusicServerError("Cannot delete playlist")
        return True

    def rate_playlist(self, playlist_id, status):
        self.rated_playlists.append((playlist_id, status))
        return {"actions": []}

    def get_playlist(self, playlist_id, limit=None):
        self.loaded_playlists.append(playlist_id)
        return {"id": playlist_id, "title": "Episodes for Later", "tracks": []}

    def remove_playlist_items(self, playlist_id, playlist_episodes):
        self.removed_playlist_items.append((playlist_id, playlist_episodes))
        return "STATUS_SUCCEEDED"


class TestDeletePlaylists:
    def test_deletes_all_playlists_when_no_selectors_are_provided(self):
        yt_music = FakePlaylistYTMusic(
            [
                make_playlist("Keep Moving", "P1"),
                make_playlist("Road Trip", "P2"),
                make_playlist("Liked Music", "LM"),
            ]
        )
        ctx = ActionContext(yt_music, static_progress=True)

        result = delete_playlists(ctx)

        assert result == (2, 3)
        assert yt_music.deleted_playlists == ["P1", "P2"]
        assert yt_music.loaded_playlists == ["SE"]

    def test_deletes_only_selected_playlist_title(self):
        yt_music = FakePlaylistYTMusic(
            [
                make_playlist("Keep Moving", "P1"),
                make_playlist("Road Trip", "P2"),
            ]
        )
        ctx = ActionContext(yt_music, static_progress=True)

        result = delete_playlists(ctx, playlist_selectors=("road trip",))

        assert result == (1, 1)
        assert yt_music.deleted_playlists == ["P2"]
        assert yt_music.loaded_playlists == []

    def test_playlist_id_selects_one_playlist_when_titles_are_duplicated(self):
        yt_music = FakePlaylistYTMusic(
            [
                make_playlist("Road Trip", "P1"),
                make_playlist("Road Trip", "P2"),
            ]
        )
        ctx = ActionContext(yt_music, static_progress=True)

        result = delete_playlists(ctx, playlist_selectors=("P2",))

        assert result == (1, 1)
        assert yt_music.deleted_playlists == ["P2"]

    def test_missing_selector_raises_before_deleting_anything(self):
        yt_music = FakePlaylistYTMusic([make_playlist("Road Trip", "P1")])
        ctx = ActionContext(yt_music, static_progress=True)

        with pytest.raises(ValueError, match="No playlist found"):
            delete_playlists(ctx, playlist_selectors=("Missing",))

        assert yt_music.deleted_playlists == []

    def test_duplicate_title_selector_raises_before_deleting_anything(self):
        yt_music = FakePlaylistYTMusic(
            [
                make_playlist("Road Trip", "P1"),
                make_playlist("Road Trip", "P2"),
            ]
        )
        ctx = ActionContext(yt_music, static_progress=True)

        with pytest.raises(ValueError, match="Multiple playlists named"):
            delete_playlists(ctx, playlist_selectors=("Road Trip",))

        assert yt_music.deleted_playlists == []

    def test_auto_playlist_selector_raises_before_deleting_anything(self):
        yt_music = FakePlaylistYTMusic(
            [
                make_playlist("Liked Music", "LM"),
                make_playlist("Road Trip", "P1"),
            ]
        )
        ctx = ActionContext(yt_music, static_progress=True)

        with pytest.raises(ValueError, match="Cannot delete auto playlist"):
            delete_playlists(ctx, playlist_selectors=("LM",))

        assert yt_music.deleted_playlists == []

    def test_falls_back_to_rate_playlist_when_delete_raises_server_error(self):
        yt_music = FakePlaylistYTMusic(
            [
                make_playlist("Community Playlist", "C1"),
                make_playlist("Owned Playlist", "P1"),
            ],
            delete_playlist_errors={"C1"},
        )
        ctx = ActionContext(yt_music, static_progress=True)

        result = delete_playlists(ctx)

        assert result == (2, 2)
        assert yt_music.deleted_playlists == ["C1", "P1"]
        assert yt_music.rated_playlists == [("C1", LikeStatus.INDIFFERENT)]


class TestDeleteHistory:
    def test_returns_when_watch_history_is_disabled(self, caplog):
        class FakeYTMusic:
            def get_history(self):
                raise YTMusicServerError({"text": "Turn on your YouTube watch history to keep track of what you watch"})

        ctx = ActionContext(FakeYTMusic(), static_progress=True)

        with caplog.at_level(logging.WARNING):
            items_deleted = delete_history(ctx, items_deleted=3)

        warning_messages = [record.getMessage() for record in caplog.records if record.levelno == logging.WARNING]
        assert items_deleted == 3
        assert "Your watch history is turned off, nothing to delete." in warning_messages

    def test_reraises_unexpected_server_errors(self):
        class FakeYTMusic:
            def get_history(self):
                raise YTMusicServerError("Server returned HTTP 401: Unauthorized.")

        ctx = ActionContext(FakeYTMusic(), static_progress=True)

        with pytest.raises(YTMusicServerError, match="401"):
            delete_history(ctx)

    def test_returns_when_history_is_empty(self, caplog):
        class FakeYTMusic:
            def get_history(self):
                raise Exception("None")

        ctx = ActionContext(FakeYTMusic(), static_progress=True)

        with caplog.at_level(logging.INFO):
            items_deleted = delete_history(ctx, items_deleted=2)

        info_messages = [record.getMessage() for record in caplog.records if record.levelno == logging.INFO]
        assert items_deleted == 2
        assert "History is empty, nothing left to delete." in info_messages
        assert "Deleted 2 history items." in info_messages

    def test_reraises_unexpected_non_server_errors(self):
        class FakeYTMusic:
            def get_history(self):
                raise RuntimeError("boom")

        ctx = ActionContext(FakeYTMusic(), static_progress=True)

        with pytest.raises(RuntimeError, match="boom"):
            delete_history(ctx)
