import ytmusicapi
from generated.ui_playlist_selection_dialog import Ui_PlaylistSelectionDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtWidgets import QMessageBox


class DeletePlaylistsDialog(QDialog, Ui_PlaylistSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlists to Delete")
        self.radioButtonLabel.setVisible(False)
        self.radioButtonA.setVisible(False)
        self.radioButtonB.setVisible(False)
        self.scoreCutoffInput.setVisible(False)
        self.scoreCutoffLabel.setVisible(False)
        self.infoButton.setVisible(False)
        self.playlistIdLabel.setVisible(False)
        self.playlistIdInput.setVisible(False)
        self.playlistIdInfoButton.setVisible(False)
        self.playlistList.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)
        self.enable_ok_button()

        try:
            self.all_playlists = parent.ytmusic.get_library_playlists(limit=None)
        except (ytmusicapi.exceptions.YTMusicError, TypeError) as e:
            self.parentWidget().message(str(e))
            raise
        if not self.all_playlists:
            QMessageBox.critical(
                self,
                "Error",
                "No playlists found in your library! Your credentials may be expired. "
                "Try signing out and signing back in.",
            )
            self.close()
            self.deleteLater()
            return
        for playlist in self.all_playlists:
            item = QListWidgetItem(playlist["title"])
            item.setData(Qt.ItemDataRole.UserRole, playlist["playlistId"])
            self.playlistList.addItem(item)

    def accept(self):
        selected_playlists = self.playlistList.selectedItems()
        if not selected_playlists:
            QMessageBox.critical(self, "Error", "No playlists selected!")
            return

        confirmed = QMessageBox.warning(
            self,
            "Delete selected playlists?",
            f"This will delete {len(selected_playlists)} selected playlist(s).",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if confirmed != QMessageBox.StandardButton.Ok:
            return

        delete_playlist_args = ["delete-playlists"]
        delete_playlist_args.extend(
            playlist.data(Qt.ItemDataRole.UserRole) or playlist.text() for playlist in selected_playlists
        )
        self.parentWidget().launch_process(delete_playlist_args)
        super().accept()

    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(len(self.playlistList.selectedItems()) > 0)
