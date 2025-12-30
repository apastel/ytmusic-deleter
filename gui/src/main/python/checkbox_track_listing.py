import re
from typing import Dict
from typing import List

import requests
from generated.ui_checkbox_track_listing import Ui_CheckboxTrackListingDialog
from PySide6.QtCore import Property
from PySide6.QtCore import QEvent
from PySide6.QtCore import QPoint
from PySide6.QtCore import QRect
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColorConstants
from PySide6.QtGui import QImage
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem

ARTWORK_DATA_INDEX = 4


class CheckboxTrackListingDialog(QDialog, Ui_CheckboxTrackListingDialog):
    def __init__(self, parent, dupe_groups: List[List[Dict]]):
        super().__init__(parent)
        self.setupUi(self)

        self.dupe_groups = dupe_groups
        self.okCancelbuttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("Finish")
        self.tableWidget = CheckboxTableWidget(self)
        self.leftButton.setEnabled(False)
        self.rightButton.setEnabled(False)
        self.tableWidget.table_idx_changed.connect(self.on_table_idx_changed)
        self.leftButton.clicked.connect(self.left_button_clicked)
        self.rightButton.clicked.connect(self.right_button_clicked)
        self.tableWidget.table_idx = 0

        self.items_to_remove = []

    @Slot()
    def left_button_clicked(self):
        self.tableWidget.table_idx -= 1

    @Slot()
    def right_button_clicked(self):
        self.tableWidget.table_idx += 1

    def on_table_idx_changed(self, new_idx):
        self.tableWidget.setRowCount(0)
        self.tableWidget.repopulate_table()
        self.leftButton.setEnabled(new_idx > 0)
        self.rightButton.setEnabled(new_idx < (len(self.dupe_groups) - 1))
        self.pageNumberLabel.setText(f"Page {new_idx + 1} of {len(self.dupe_groups)}")

    def accept(self):
        super().accept()

    def reject(self):
        super().reject()


class CheckboxTableWidget(QTableWidget):
    table_idx_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)
        self.setGeometry(QRect(30, 50, 860, 440))
        self._table_idx = -1
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cellChanged.connect(self.on_cell_changed)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Remove?", "Artist", "Title", "Album", "Duration", "Artwork"])
        self._artwork_popup = None
        self.artwork_column = 5

    @Property(int, notify=table_idx_changed)
    def table_idx(self):
        return self._table_idx

    @table_idx.setter
    def table_idx(self, value):
        if self._table_idx != value:
            self._table_idx = value
            self.table_idx_changed.emit(self._table_idx)

    def repopulate_table(self):
        for row_idx, track in enumerate(self.parentWidget().dupe_groups[self.table_idx]):
            data_list: List[str] = [
                track["artist"],
                track["title"],
                track["album"],
                track["duration"],
                track["thumbnail"],
            ]
            row_items: List[QTableWidgetItem] = [QTableWidgetItem(data) for data in data_list]

            # Insert the blank row
            self.insertRow(row_idx)

            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox_item.setCheckState(
                Qt.CheckState.Checked
                if self.parentWidget().dupe_groups[self.table_idx][row_idx].get("checked", False)
                else Qt.CheckState.Unchecked
            )
            checkbox_item.setBackground(QBrush(QColorConstants.Gray))
            self.setItem(row_idx, 0, checkbox_item)

            for col_idx, item in enumerate(row_items):
                if col_idx == ARTWORK_DATA_INDEX:
                    thumbnail_url = data_list[ARTWORK_DATA_INDEX]
                    # Store larger version for popup
                    large_url = self._resize_google_thumb(thumbnail_url, 300, 300)
                    r_large = requests.get(large_url)
                    large_img = QImage()
                    large_img.loadFromData(r_large.content)
                    large_pixmap = QPixmap.fromImage(large_img)

                    # Small thumbnail for cell
                    thumb = QPixmap.fromImage(large_img).scaled(
                        64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    )

                    item.setIcon(thumb)
                    item.setSizeHint(QSize(64, 64))
                    item.setText("")

                    # Store large pixmap for popup (keyed by row)
                    item.setData(Qt.ItemDataRole.UserRole, large_pixmap)

                # Set items in the new row
                self.setItem(row_idx, col_idx + 1, item)

        self.resizeColumnsToContents()

    def _resize_google_thumb(self, url: str, width: int, height: int) -> str:
        if "w" in url and "-h" in url:
            return re.sub(r"w\d+-h\d+", f"w{width}-h{height}", url)
        return url  # fallback: unchanged

    @Slot(int, int)
    def on_cell_changed(self, row, col):
        if col != 0:
            # Not a checkbox
            return
        if self.item(row, col).checkState() == Qt.Checked:
            self.parentWidget().dupe_groups[self.table_idx][row]["checked"] = True
        elif self.item(row, col).checkState() == Qt.Unchecked:
            self.parentWidget().dupe_groups[self.table_idx][row]["checked"] = False

    def eventFilter(self, obj, event):
        """
        Filters mouse hover events on the viewport to show/hide artwork preview popup.

        Handles HoverEnter, HoverMove, and MouseMove events over artwork cells (column 5)
        to display a larger version of the thumbnail image stored in UserRole data.

        - Shows crisp 300x300 artwork popup instantly on hover
        - Hides immediately when mouse leaves artwork column
        - Prevents stuck/orphaned popups during fast mouse movement

        Returns True if event was handled, False to continue normal processing.
        """
        if obj == self.viewport() and event.type() in [
            QEvent.Type.HoverEnter,
            QEvent.Type.HoverMove,
            QEvent.Type.MouseMove,
        ]:

            pos = event.pos()
            index = self.indexAt(pos)

            # Hide if not over artwork
            if self._artwork_popup and self._artwork_popup.isVisible():
                if not (index.isValid() and index.column() == self.artwork_column):
                    self._artwork_popup.hide()
                    return True

            # Show if over artwork - use stored large pixmap
            if index.isValid() and index.column() == self.artwork_column:
                item = self.item(index.row(), index.column())
                if item:
                    large_pixmap = item.data(Qt.ItemDataRole.UserRole)
                    if large_pixmap and not large_pixmap.isNull():
                        if self._artwork_popup is None:
                            self._artwork_popup = QLabel(self.viewport())
                            self._artwork_popup.setWindowFlags(Qt.WindowType.ToolTip)
                            self._artwork_popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

                        self._artwork_popup.setPixmap(large_pixmap)
                        self._artwork_popup.adjustSize()
                        self._artwork_popup.move(event.globalPos() + QPoint(10, 10))
                        self._artwork_popup.show()
                        return True

            return False

        return super().eventFilter(obj, event)
