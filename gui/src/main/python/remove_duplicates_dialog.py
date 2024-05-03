from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QMessageBox


class RemoveDuplicatesDialog(QDialog, Ui_PlaylistSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlist to De-dupe")
        self.enable_ok_button()
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)
        self.shuffleCheckBox.hide()

        playlists = parent.ytmusic.get_library_playlists()
        self.playlistList.insertItems(0, [playlist["title"] for playlist in playlists])

    def accept(self):
        selected_playlist = self.playlistList.selectedItems()
        if not selected_playlist:
            QMessageBox.critical(self, "Error", "No playlist selected!")
            return
        remove_dupes_args = ["remove-duplicates"] + [selected_playlist[0].text()]
        self.parentWidget().launch_process(remove_dupes_args)

    @Slot()
    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.playlistList.selectedItems()) > 0)
