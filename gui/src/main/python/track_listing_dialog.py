from typing import List

import requests
from generated.ui_track_listing import Ui_TrackListingDialog
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QTableWidgetItem


class TrackListingDialog(QDialog, Ui_TrackListingDialog):
    def __init__(self, parent, tracklist, show_thumbnail: bool = True):
        super().__init__(parent)
        self.setupUi(self)

        self.tracklist = tracklist

        for row_idx, track in enumerate(tracklist):
            data_list: List[str] = [
                track["artist"],
                track["title"],
                track["album"],
                track["duration"],
                track["thumbnail"],
            ]
            row_items: List[QTableWidgetItem] = [QTableWidgetItem(data) for data in data_list]

            # Insert the blank row
            self.trackListTable.insertRow(row_idx)
            for col_idx, item in enumerate(row_items):
                if col_idx == 4:
                    item.setSizeHint(QSize(64, 64))
                    item.setText("")
                    if show_thumbnail:
                        r = requests.get(data_list[4])
                        img = QImage()
                        img.loadFromData(r.content)
                        pixmap = QPixmap.fromImage(img)
                        item.setIcon(pixmap)
                # Set items in the new row
                self.trackListTable.setItem(row_idx, col_idx, item)

        self.trackListTable.resizeColumnsToContents()

    def accept(self):
        super().accept()

    def reject(self):
        super().reject()
