from generated.ui_add_all_to_playlist_dialog import Ui_AddAllSongsToPlaylistDialog
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QStyle


class AddAllToPlaylistDialog(QDialog, Ui_AddAllSongsToPlaylistDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Add All Songs To Playlist(s)")
        self.radioButtonLabel.setText("Add all songs from...")
        self.infoButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.infoButton.clicked.connect(self.show_info_dialog)

    def accept(self):
        library_or_uploads = self.radioButtonGroup.checkedButton().text().lower()
        max_playlist_size = self.maxPlaylistSizeBox.value()
        add_all_args = ["add-all-to-playlist", f"--{library_or_uploads}", "-m", max_playlist_size]
        self.parentWidget().launch_process(add_all_args)

    def show_info_dialog(self):
        QMessageBox.information(
            self,
            "Information",
            "This will either add all of your uploads or all of your library songs to a new playlist depending "
            "on which option you select.\n\n"
            "If you wish to combine it with one of your pre-existing playlists, you can go into YouTube Music "
            "afterwards and save the playlist to another playlist.\n\n"
            "The 'Max Playlist Size' determines how many songs will be added to a single playlist. If the number "
            "of songs exceeds the maximum, then multiple playlists will be created.\n"
            "The max value of 5000 is a YouTube Music restriction that cannot be exceeded.",
        )
