import ytmusicapi
from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from progress_worker_dialog import ProgressWorkerDialog
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QStyle
from ytmusic_deleter import common
from ytmusic_deleter.duplicates import check_for_duplicates
from ytmusic_deleter.duplicates import determine_tracks_to_remove
from ytmusicapi import YTMusic

from .checkbox_track_listing import CheckboxTrackListingDialog
from .track_listing_dialog import TrackListingDialog


class RemoveDuplicatesDialog(QDialog, Ui_PlaylistSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlist(s) to De-dupe")
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("Next")

        # Enable multiple selection in the list widget
        self.playlistList.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.enable_ok_button()
        self.enable_score_cutoff()
        self.radioButtonLabel.setText("Matching Algorithm:")
        self.radioButtonA.setText("Strict")
        self.radioButtonB.setText("Fuzzy")
        self.playlistIdLabel.setVisible(False)
        self.playlistIdInput.setVisible(False)
        self.playlistIdInfoButton.setVisible(False)
        self.radioButtonB.toggled.connect(self.enable_score_cutoff)
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)
        self.infoButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.infoButton.clicked.connect(self.show_info_dialog)

        try:
            self.all_playlists = parent.ytmusic.get_library_playlists(limit=None)
        except (ytmusicapi.exceptions.YTMusicError, TypeError) as e:
            # Ensure we log an exception in the console (not just log file) if fetching playlists fails
            self.parentWidget().message(str(e))
            raise
        if not self.all_playlists:
            QMessageBox.critical(
                self,
                "Error",
                "No playlists found in your library! Your credentials may be expired. Try signing out and signing back in.",
            )
            self.close()
            self.deleteLater()
            return
        self.playlistList.insertItems(0, [playlist["title"] for playlist in self.all_playlists])

    def accept(self):
        selected_items = self.playlistList.selectedItems()
        if not selected_items:
            QMessageBox.critical(self, "Error", "No playlist selected!")
            return

        selected_titles = [item.text() for item in selected_items]
        self.launch_remove_dupes(selected_titles)

    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(len(self.playlistList.selectedItems()) > 0)

    def enable_score_cutoff(self):
        self.scoreCutoffLabel.setEnabled(self.radioButtonB.isChecked())
        self.scoreCutoffInput.setEnabled(self.radioButtonB.isChecked())

    def show_info_dialog(self):
        QMessageBox.information(
            self,
            "Matching Algorithm",
            "Strict matching [default] will search for duplicates using string comparison "
            "after normalizing the artist and title. It should find most of your duplicates.\n\n"
            "For example, the following two tracks will be considered duplicates:\n"
            "The Offspring - 'Come Out and Play'\n"
            "The Offspring - 'Come out and play (2008 Remaster)'\n\n"
            "Try fuzzy matching to find duplicates that may be named differently. The score cutoff value "
            "determines how strict to be with the fuzzy matching. "
            "The higher the score cutoff, the more likely a match will be thrown out.\n"
            "For example, the following two track titles have a match score of 90:\n"
            "'Toms Diner'\n"
            "'Tom's Diner [Long Version] DNA feat. Suzanne Vega (1990)'\n\n"
            "A score cutoff above 90 will throw this match away. Values below 85 will likely yield too many false matches.\n"
            "The default score-cutoff is recommended but you may experiment with higher or lower values.\n"
            "The score-cutoff value is used for both artist matching and title matching.\n\n"
            "In both cases, tracks that are *exact* duplicates (same ID) will be de-duped.",
        )

    def launch_remove_dupes(self, selected_playlist_titles):
        self.selected_playlist_titles = selected_playlist_titles
        ProgressWorkerDialog("Loading playlist(s)", self).run(
            self._get_playlists, on_done=self._handle_playlists_result
        )

    def _get_playlists(self):
        yt_auth: YTMusic = self.parent().ytmusic
        playlists = []

        for title in self.selected_playlist_titles:
            selected_playlist_id = next(
                (
                    playlist["playlistId"]
                    for playlist in self.all_playlists
                    if playlist.get("title").lower() == title.lower()
                ),
                None,
            )
            if not selected_playlist_id:
                raise Exception(f"Playlist {title!r} not found")

            playlist = yt_auth.get_playlist(selected_playlist_id, limit=None)
            if not common.can_edit_playlist(playlist):
                raise Exception(f"Cannot modify playlist {title!r}. You are not the owner of this playlist.")
            playlists.append(playlist)

        return (playlists, yt_auth)

    def _handle_playlists_result(self, result):
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result), QMessageBox.StandardButton.Ok)
            return
        self.playlists, self.yt_auth = result
        ProgressWorkerDialog("Checking for duplicates", self).run(
            self._calculate_dupes, on_done=self._handle_dupe_result
        )

    def _calculate_dupes(self):
        duplicates = check_for_duplicates(
            self.playlists, self.yt_auth, self.radioButtonB.isChecked(), self.scoreCutoffInput.value()
        )
        if not duplicates:
            titles_str = ", ".join(self.selected_playlist_titles)
            raise Exception(
                f"No duplicates found in selected playlist(s): {titles_str}. "
                "If you think this is an error, open an issue on GitHub or message on Discord"
            )
        return determine_tracks_to_remove(duplicates)

    def _handle_dupe_result(self, result):
        if isinstance(result, Exception):
            QMessageBox.warning(self, "No duplicates", str(result), QMessageBox.StandardButton.Ok)
            return
        items_to_remove, remaining_dupe_groups = result

        # Step 3: Show interactive dialog
        self.track_listing_dialog = TrackListingDialog(self, items_to_remove)
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

            # Group items by playlist_id for removal
            items_by_playlist = {}
            for item in items_to_remove:
                pid = item.get("_playlist_id")
                if pid:
                    items_by_playlist.setdefault(pid, []).append(item)
                else:
                    self.parentWidget().message(f"Playlist ID is missing for track {item.get('title')}.")

            removed_count = 0
            for playlist_id, items in items_by_playlist.items():
                if playlist_id == "LM":
                    for song in items:
                        success = common.unlike_song(self.yt_auth, song)
                        if success:
                            removed_count += 1
                            dialog.set_progress(removed_count, f"Removed {removed_count} out of {total} duplicates...")
                        else:
                            self.parentWidget().message(
                                f"Failed to unlike {song.get('artist')} - {song.get('title')!r}"
                            )
                else:
                    for chunk in common.chunked(items, 50):
                        try:
                            self.yt_auth.remove_playlist_items(playlist_id, chunk)
                            removed_count += len(chunk)
                            display_count = min(removed_count, total)
                            dialog.set_progress(display_count, f"Removed {display_count} out of {total} duplicates...")
                        except Exception as e:
                            self.parentWidget().message(f"Failed to remove batch from {playlist_id}: {e}")

            titles_str = ", ".join(self.selected_playlist_titles)
            return f"{removed_count} tracks were removed from {titles_str}"

        def run_deletion():
            dialog = ProgressWorkerDialog("Removing duplicates", self, maximum=len(items_to_remove))

            def work():
                return do_deletion_with_progress(dialog)

            dialog.run(work, on_done=self._after_deletion)

        run_deletion()

    def _after_deletion(self, result):
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result), QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(self, "Finished!", str(result), QMessageBox.StandardButton.Ok)
