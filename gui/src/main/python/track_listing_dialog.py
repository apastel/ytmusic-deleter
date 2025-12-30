from typing import List

from generated.ui_track_listing import Ui_TrackListingDialog
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QTableWidgetItem
from tracklist_table_widget import TracklistTableWidget

ARTWORK_COLUMN_INDEX = 4


class TrackListingDialog(QDialog, Ui_TrackListingDialog):
    def __init__(self, parent, tracklist):
        super().__init__(parent)
        self.setupUi(self)
        self.tracklistTable = TracklistTableWidget(ARTWORK_COLUMN_INDEX, self)
        self.tracklistTable.setGeometry(QRect(30, 70, 860, 440))
        self.tracklistTable.setColumnCount(6)
        self.tracklistTable.setHorizontalHeaderLabels(["Artist", "Title", "Album", "Duration", "Thumbnail", "Type"])
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Skip")

        self.tracklist = tracklist

        for row_idx, track in enumerate(tracklist):
            data_list: List[str] = [
                track["artist"],
                track["title"],
                track["album"],
                track["duration"],
                track["thumbnail"],
                track["videoType"],
            ]
            row_items: List[QTableWidgetItem] = [QTableWidgetItem(data) for data in data_list]

            # Insert the blank row
            self.tracklistTable.insertRow(row_idx)
            for col_idx, item in enumerate(row_items):
                self.tracklistTable.update_item(col_idx, item)
                self.tracklistTable.setItem(row_idx, col_idx, item)

        self.tracklistTable.set_max_column_widths()

    def accept(self):
        super().accept()

    def reject(self):
        super().reject()
