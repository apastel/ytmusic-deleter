from generated.ui_sort_playlists_dialog import Ui_SortPlaylistsDialog
from PySide6.QtWidgets import QDialog


class SortPlaylistsDialog(QDialog, Ui_SortPlaylistsDialog):
    def __init__(self):
        super(SortPlaylistsDialog, self).__init__()
        self.setupUi(self)
