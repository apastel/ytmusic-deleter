from generated.ui_checkbox_track_listing import Ui_CheckboxTrackListingDialog
from PySide6.QtCore import Property
from PySide6.QtCore import QRect
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColorConstants
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QTableWidgetItem

from .tracklist_table_widget import TracklistTableWidget

ARTWORK_COLUMN_INDEX = 5


class CheckboxTrackListingDialog(QDialog, Ui_CheckboxTrackListingDialog):
    def __init__(self, parent, dupe_groups: list[list[dict]]):
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


class CheckboxTableWidget(TracklistTableWidget):
    table_idx_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(ARTWORK_COLUMN_INDEX, parent)
        self.setGeometry(QRect(30, 50, 860, 440))
        self._table_idx = -1
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cellChanged.connect(self.on_cell_changed)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(["Remove?", "Artist", "Title", "Album", "Duration", "Thumbnail", "Type"])

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
            data_list: list[str] = [
                track["artist"],
                track["title"],
                track["album"],
                track["duration"],
                track["thumbnail"],
                track["videoType"],
            ]
            row_items: list[QTableWidgetItem] = [QTableWidgetItem(data) for data in data_list]

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
                self.update_item(col_idx + 1, item)
                self.setItem(row_idx, col_idx + 1, item)

        self.set_max_column_widths()

    @Slot(int, int)
    def on_cell_changed(self, row, col):
        if col != 0:
            # Not a checkbox
            return
        cell_item = self.item(row, col)
        if cell_item is not None:
            if cell_item.checkState() == Qt.CheckState.Checked:
                self.parentWidget().dupe_groups[self.table_idx][row]["checked"] = True
            elif cell_item.checkState() == Qt.CheckState.Unchecked:
                self.parentWidget().dupe_groups[self.table_idx][row]["checked"] = False
