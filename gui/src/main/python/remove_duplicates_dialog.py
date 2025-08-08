import ytmusicapi
from checkbox_track_listing import CheckboxTrackListingDialog
from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from progress_worker_dialog import ProgressWorkerDialog
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QMessageBox
from track_listing_dialog import TrackListingDialog
from ytmusic_deleter.common import can_edit_playlist
from ytmusic_deleter.common import chunked
from ytmusic_deleter.common import INDIFFERENT
from ytmusic_deleter.duplicates import check_for_duplicates
from ytmusic_deleter.duplicates import determine_tracks_to_remove
from ytmusicapi import YTMusic


class RemoveDuplicatesDialog(QDialog, Ui_PlaylistSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlist to De-dupe")
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Next")
        self.enable_ok_button()
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)
        self.radioButtonLabel.setVisible(False)
        self.radioButtonLibrary.setVisible(False)
        self.radioButtonUploads.setVisible(False)

        try:
            self.all_playlists = parent.ytmusic.get_library_playlists(limit=None)
        except (ytmusicapi.exceptions.YTMusicError, TypeError) as e:
            # Ensure we log an exception in the console (not just log file) if fetching playlists fails
            self.parentWidget().message(str(e))
            raise
        self.playlistList.insertItems(0, [playlist["title"] for playlist in self.all_playlists])

    def accept(self):
        selected_playlist = self.playlistList.selectedItems()
        if not selected_playlist:
            QMessageBox.critical(self, "Error", "No playlist selected!")
            return
        self.launch_remove_dupes(selected_playlist[0].text())

    @Slot()
    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.playlistList.selectedItems()) > 0)

    def launch_remove_dupes(self, selected_playlist_title):
        self.selected_playlist_title = selected_playlist_title
        ProgressWorkerDialog("Loading playlist", self).run(self._get_playlist, on_done=self._handle_playlist_result)

    def _get_playlist(self):
        selected_playlist_id = next(
            (
                playlist["playlistId"]
                for playlist in self.all_playlists
                if playlist.get("title").lower() == self.selected_playlist_title.lower()
            ),
            None,
        )
        if not selected_playlist_id:
            raise Exception("Playlist not found")
        yt_auth: YTMusic = self.parent().ytmusic
        playlist = yt_auth.get_playlist(selected_playlist_id, limit=None)
        if not can_edit_playlist(playlist):
            raise Exception(
                f"Cannot modify playlist {self.selected_playlist_title!r}. You are not the owner of this playlist."
            )
        return (playlist, yt_auth, selected_playlist_id)

    def _handle_playlist_result(self, result):
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result), QMessageBox.Ok)
            return
        self.playlist, self.yt_auth, self.selected_playlist_id = result
        ProgressWorkerDialog("Checking for duplicates", self).run(
            self._calculate_dupes, on_done=self._handle_dupe_result
        )

    def _calculate_dupes(self):
        duplicates = check_for_duplicates(self.playlist, self.yt_auth)
        if not duplicates:
            raise Exception(
                f"No duplicates found in playlist {self.selected_playlist_title!r}. "
                "If you think this is an error, open an issue on GitHub or message on Discord"
            )
        return determine_tracks_to_remove(duplicates)

    def _handle_dupe_result(self, result):
        if isinstance(result, Exception):
            QMessageBox.warning(self, "No duplicates", str(result), QMessageBox.Ok)
            return
        items_to_remove, remaining_dupe_groups = result

        # Step 3: Show interactive dialog
        self.track_listing_dialog = TrackListingDialog(self, items_to_remove, show_thumbnail=False)
        ok_clicked = self.track_listing_dialog.exec()
        if not ok_clicked:
            items_to_remove = []

        # If there are similar dupes, show another dialog
        if remaining_dupe_groups:
            self.checkbox_track_listing_dialog = CheckboxTrackListingDialog(self, remaining_dupe_groups)
            ok_clicked = self.checkbox_track_listing_dialog.exec()
            if not ok_clicked:
                return
            selected_tracks = [
                item
                for sublist in self.checkbox_track_listing_dialog.dupe_groups
                for item in sublist
                if item.get("checked", False)
            ]
            items_to_remove.extend(selected_tracks)

        # Step 4: Do deletion (show wait dialog)
        def do_deletion_with_progress(dialog):
            if not items_to_remove:
                return "No duplicate tracks were marked for deletion."
            total = len(items_to_remove)
            removed = 0
            if self.playlist.get("id") == "LM":
                for i, song in enumerate(items_to_remove, 1):
                    self.yt_auth.rate_song(song["videoId"], INDIFFERENT)
                    dialog.set_progress(i, f"Removed {i} out of {total} duplicates...")
            else:
                for i, chunk in enumerate(chunked(items_to_remove, 50), 1):
                    self.yt_auth.remove_playlist_items(self.selected_playlist_id, chunk)
                    removed = min(i * 50, total)
                    dialog.set_progress(removed, f"Removed {removed} out of {total} duplicates...")
            return f"{total} tracks were removed from {self.selected_playlist_title!r}"

        def run_deletion():
            dialog = ProgressWorkerDialog("Removing duplicates", self, maximum=len(items_to_remove))

            def work():
                return do_deletion_with_progress(dialog)

            dialog.run(work, on_done=self._after_deletion)

        run_deletion()

    def _after_deletion(self, result):
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result), QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Finished!", str(result), QMessageBox.Ok)
