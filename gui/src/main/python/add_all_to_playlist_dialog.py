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
        self.shuffleCheckBox.hide()

        self.all_playlists = parent.ytmusic.get_library_playlists(limit=None)
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
