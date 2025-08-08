import ytmusicapi
from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QMessageBox


class AddAllToPlaylistDialog(QDialog, Ui_PlaylistSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlist to Add All Songs To")
        self.enable_ok_button()
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)

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
        selected_playlist = self.playlistList.selectedItems()
        if not selected_playlist:
            QMessageBox.critical(self, "Error", "No playlist selected!")
            return
        library_or_uploads = self.radioButtonGroup.checkedButton().text().lower()
        add_all_args = ["add-all-to-playlist", selected_playlist[0].text()] + [f"--{library_or_uploads}"]
        self.parentWidget().launch_process(add_all_args)

    @Slot()
    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.playlistList.selectedItems()) > 0)
