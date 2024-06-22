from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QMessageBox


class SortPlaylistsDialog(QDialog, Ui_PlaylistSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlist(s) to Sort")
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Next")
        self.enable_ok_button()
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)
        self.playlistList.setSelectionMode(QAbstractItemView.MultiSelection)

        playlists = parent.ytmusic.get_library_playlists()
        self.playlistList.insertItems(0, [playlist["title"] for playlist in playlists])

    def accept(self):
        selected_playlists = self.playlistList.selectedItems()
        if not selected_playlists:
            QMessageBox.critical(self, "Error", "No playlists selected!")
            return
        sort_playlist_args = ["sort-playlist"] + [playlist.text() for playlist in selected_playlists]
        if self.shuffleCheckBox.isChecked():
            sort_playlist_args.insert(1, "-s")
        self.parentWidget().launch_process(sort_playlist_args)

    @Slot()
    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.playlistList.selectedItems()) > 0)
