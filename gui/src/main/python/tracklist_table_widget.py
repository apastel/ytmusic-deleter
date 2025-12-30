import re

import requests
from PySide6.QtCore import QEvent
from PySide6.QtCore import QPoint
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QImage
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QTableWidget
from ytmusicapi.models.content.enums import VideoType


class TracklistTableWidget(QTableWidget):
    table_idx_changed = Signal(int)

    def __init__(self, artwork_column_idx, parent=None):
        super().__init__(parent)
        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._artwork_popup = None
        self._artwork_column_idx = artwork_column_idx

    def set_max_column_widths(self):
        """Size columns to content, then cap at max 200px."""
        self.resizeColumnsToContents()  # natural size first

        for col in range(self.columnCount()):
            col_width = self.columnWidth(col)
            if col_width > 200:
                self.setColumnWidth(col, 200)

            # Make all columns resizable
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        # Optional: stretch last column
        last_col = self.columnCount() - 1
        self.horizontalHeader().setSectionResizeMode(last_col, QHeaderView.ResizeMode.Stretch)

    def update_item(self, col_idx, item):
        """
        Update certain row items like Artwork or Type
        """
        header_item = self.horizontalHeaderItem(col_idx)
        if not header_item:
            return
        header_text = header_item.text()
        if not header_text:
            return
        if header_text == "Artwork":
            thumbnail_url = item.text()
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
        elif header_text == "Type":
            video_type = item.text()
            match video_type:
                case VideoType.UGC:
                    type_str = "User-generated Content"
                case VideoType.ATV:
                    type_str = "Artist-uploaded Track"
                case VideoType.OMV:
                    type_str = "Official Music Video"
                case _:
                    type_str = "Unknown"
            item.setText(type_str)

    def _resize_google_thumb(self, url: str, width: int, height: int) -> str:
        if "w" in url and "-h" in url:
            return re.sub(r"w\d+-h\d+", f"w{width}-h{height}", url)
        return url

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
                if not (index.isValid() and index.column() == self._artwork_column_idx):
                    self._artwork_popup.hide()
                    return True

            # Show if over artwork - use stored large pixmap
            if index.isValid() and index.column() == self._artwork_column_idx:
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
