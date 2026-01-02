import ytmusicapi
from generated.ui_sort_playlist_dialog import Ui_SortPlaylistDialog
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtWidgets import QMessageBox


class SortPlaylistsDialog(QDialog, Ui_SortPlaylistDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Select Playlist(s) to Sort")
        self.enable_ok_button()
        self.enable_left_arrow_button()
        self.enable_right_arrow_button()
        self.playlistList.itemSelectionChanged.connect(self.enable_ok_button)
        self.shuffleCheckBox.checkStateChanged.connect(self.enable_ok_button)
        self.shuffleCheckBox.checkStateChanged.connect(self.shuffle_checked)
        self.addButton.clicked.connect(self.add_item)
        self.removeButton.clicked.connect(self.remove_item)
        self.availableAttributesListWidget.itemSelectionChanged.connect(self.enable_right_arrow_button)
        self.selectedAttributesListWidget.itemSelectionChanged.connect(self.enable_left_arrow_button)
        self.playlistList.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.original_order = ["Artist", "Album Title", "Track Title", "Duration"]
        # Populate the available list, maintaining original order
        for item_text in self.original_order:
            list_item = QListWidgetItem(item_text)
            self.availableAttributesListWidget.addItem(list_item)

        try:
            playlists = parent.ytmusic.get_library_playlists(limit=None)
        except (ytmusicapi.exceptions.YTMusicError, TypeError) as e:
            # Ensure we log an exception in the console (not just log file) if fetching playlists fails
            self.parentWidget().message(str(e))
            raise
        if not playlists:
            QMessageBox.critical(
                self,
                "Error",
                "No playlists found in your library! Your credentials may be expired. Try signing out and signing back in.",
            )
            self.close()
            self.deleteLater()
            return
        self.playlistList.insertItems(0, [playlist["title"] for playlist in playlists])

    def accept(self):
        selected_playlists = self.playlistList.selectedItems()
        if not selected_playlists:
            QMessageBox.critical(self, "Error", "No playlists selected!")
            return
        sort_playlist_args = ["sort-playlist"] + [playlist.text() for playlist in selected_playlists]
        if self.shuffleCheckBox.isChecked():
            sort_playlist_args.append("--shuffle")
        else:
            item_list = []
            for i in range(self.selectedAttributesListWidget.count()):
                item_list.append(self.selectedAttributesListWidget.item(i).text())
            custom_sort_args = []
            for attr in item_list:
                custom_sort_args = custom_sort_args + ["--custom-sort", attr.replace(" ", "_").lower()]
            sort_playlist_args = sort_playlist_args + custom_sort_args
            if self.reverseCheckbox.isChecked():
                sort_playlist_args.append("--reverse")
        self.parentWidget().launch_process(sort_playlist_args)
        super().accept()

    @Slot()
    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            len(self.playlistList.selectedItems()) > 0
            and (self.selectedAttributesListWidget.count() > 0 or self.shuffleCheckBox.isChecked())
        )

    @Slot()
    def enable_right_arrow_button(self):
        self.addButton.setEnabled(len(self.availableAttributesListWidget.selectedItems()) > 0)

    @Slot()
    def enable_left_arrow_button(self):
        self.removeButton.setEnabled(len(self.selectedAttributesListWidget.selectedItems()) > 0)

    @Slot()
    def shuffle_checked(self):
        self.availableAttributesListWidget.clearSelection()
        self.selectedAttributesListWidget.clearSelection()
        self.availableAttributesListWidget.setDisabled(self.shuffleCheckBox.isChecked())
        self.selectedAttributesListWidget.setDisabled(self.shuffleCheckBox.isChecked())
        self.addButton.setDisabled(self.shuffleCheckBox.isChecked())
        self.removeButton.setDisabled(self.shuffleCheckBox.isChecked())
        self.reverseCheckbox.setDisabled(self.shuffleCheckBox.isChecked())

    @Slot()
    def add_item(self):
        selected_item = self.availableAttributesListWidget.currentItem()
        if selected_item:
            item_text = selected_item.text()
            list_item = QListWidgetItem(item_text)
            self.selectedAttributesListWidget.addItem(list_item)
            self.availableAttributesListWidget.takeItem(self.availableAttributesListWidget.row(selected_item))
            self.shuffleCheckBox.setChecked(False)
            self.enable_ok_button()

    @Slot()
    def remove_item(self):
        selected_item = self.selectedAttributesListWidget.currentItem()
        if selected_item:
            item_text = selected_item.text()
            list_item = QListWidgetItem(item_text)
            self.availableAttributesListWidget.insertItem(self.original_order.index(item_text), list_item)
            self.selectedAttributesListWidget.takeItem(self.selectedAttributesListWidget.row(selected_item))
            self.enable_ok_button()
