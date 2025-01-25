import ytmusicapi
from checkbox_track_listing import CheckboxTrackListingDialog
from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QMessageBox
from track_listing_dialog import TrackListingDialog
from ytmusic_deleter.common import can_edit_playlist
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
        self.shuffleCheckBox.hide()
        self.radioButtonLabel.setVisible(False)
        self.radioButtonLibrary.setVisible(False)
        self.radioButtonUploads.setVisible(False)

        try:
            self.all_playlists = parent.ytmusic.get_library_playlists(limit=None)
        except ytmusicapi.exceptions.YTMusicError as e:
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
        # Get playlist
        selected_playlist_id = next(
            (
                playlist["playlistId"]
                for playlist in self.all_playlists
                if playlist.get("title").lower() == selected_playlist_title.lower()
            ),
            None,
        )
        if not selected_playlist_id:
            # alert that playlist selection was invalid somehow
            raise Exception
        yt_auth: YTMusic = self.parent().ytmusic
        playlist = yt_auth.get_playlist(selected_playlist_id, limit=None)

        # Ensure can edit playlist
        if not can_edit_playlist(playlist):
            warning_dialog = QMessageBox()
            warning_dialog.setIcon(QMessageBox.Warning)
            warning_dialog.setText(
                f"Cannot modify playlist {selected_playlist_title!r}. You are not the owner of this playlist."
            )
            return warning_dialog.exec()

        # Get duplicates
        duplicates = check_for_duplicates(playlist, yt_auth)
        if not duplicates:
            warning_dialog = QMessageBox()
            warning_dialog.setIcon(QMessageBox.Warning)
            warning_dialog.setText(
                f"No duplicates found in playlist {selected_playlist_title!r}. If you think this is an error open an issue on GitHub or message on Discord"  # noqa: B950
            )
            return warning_dialog.exec()

        # Check for exact dupes
        items_to_remove, remaining_dupe_groups = determine_tracks_to_remove(duplicates)
        if items_to_remove:
            self.track_listing_dialog = TrackListingDialog(self, items_to_remove)
            ok_clicked = self.track_listing_dialog.exec()
            if not ok_clicked:
                items_to_remove = []

        # Check for similar dupes
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

        # Nothing was marked for deletion
        if not items_to_remove:
            self.parent().message("Finished: No duplicate tracks were marked for deletion.")
            QMessageBox.information(self, "Finished!", "No duplicate tracks were marked for deletion.", QMessageBox.Ok)
            return

        # Proceed with deletion
        self.parent().message(f"Removing {len(items_to_remove)} tracks total from playlist {selected_playlist_title!r}")

        if playlist.get("id") == "LM":
            # This is the 'Liked Music' playlist, must use rate_song()
            for song in items_to_remove:
                yt_auth.rate_song(song["videoId"], INDIFFERENT)
        else:
            yt_auth.remove_playlist_items(selected_playlist_id, items_to_remove)
        self.parent().message("Finished: Tracks removed")

        QMessageBox.information(
            self,
            "Finished!",
            f"{len(items_to_remove)} tracks were removed from {selected_playlist_title!r}",
            QMessageBox.Ok,
        )
        return
