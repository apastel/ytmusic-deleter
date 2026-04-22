import logging

import pytest
from ytmusic_deleter.actions import ActionContext
from ytmusic_deleter.actions import delete_history
from ytmusicapi.exceptions import YTMusicServerError


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
