import ytmusicapi
from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QStyle


class AddAllToLibraryDialog(QDialog, Ui_PlaylistSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlist to Add All Songs From")
        self.radioButtonLabel.setVisible(False)
        self.radioButtonA.setVisible(False)
        self.radioButtonB.setVisible(False)
        self.scoreCutoffInput.setVisible(False)
        self.scoreCutoffLabel.setVisible(False)
        self.infoButton.setVisible(False)
        self.enable_ok_button()
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)
        self.playlistIdInput.textChanged.connect(self.enable_ok_button)
        self.playlistIdInfoButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.playlistIdInfoButton.clicked.connect(self.show_info_dialog)
        self.playlistIdInput.textChanged.connect(self.playlist_id_text_changed)

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
                "Unable to connect to your library! Your credentials may be expired. Try signing out and signing back in.",
            )
            self.close()
            self.deleteLater()
            return
        self.playlistList.insertItems(0, [playlist["title"] for playlist in self.all_playlists])

    def accept(self):
        selected_playlist = self.playlistList.selectedItems()
        is_playlistid_present = bool(self.playlistIdInput.text())
        if not (selected_playlist or is_playlistid_present):
            QMessageBox.critical(self, "Error", "No playlist selected!")
            return
        playlist_title_or_id = self.playlistIdInput.text() if is_playlistid_present else selected_playlist[0].text()
        add_all_args = ["add-all-to-library", playlist_title_or_id]
        self.parentWidget().launch_process(add_all_args)

    def show_info_dialog(self):
        QMessageBox.information(
            self,
            "Information",
            "This will add all songs from a selected playlist to your library.\n\n"
            "You can either select one of your playlists, or paste the "
            "ID of any public playlist.\n\nPlaylist IDs are obtained by viewing the playlist "
            "in your browser and copying the ID from your address bar, specifically the "
            "long alphanumeric string at the end (e.g. RDCLAK5uy_kx0d2-VPr69KAkIQOTVFq04hCBsJE9LaI).",
        )

    def enable_ok_button(self):
        is_playlist_selected = len(self.playlistList.selectedItems()) > 0
        is_playlistid_present = bool(self.playlistIdInput.text())
        ok_button = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)

        ok_button.setEnabled(is_playlist_selected or is_playlistid_present)

    def playlist_id_text_changed(self):
        self.playlistList.setDisabled(bool(self.playlistIdInput.text()))
