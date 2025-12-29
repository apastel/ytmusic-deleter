from generated import ui_delete_uploads_dialog
from PySide6 import QtCore
from PySide6 import QtWidgets


class DeleteUploadsDialog(QtWidgets.QDialog, ui_delete_uploads_dialog.Ui_DeleteUploadsDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.enable_score_cutoff()
        self.addUploadsCheckBox.checkStateChanged.connect(self.enable_score_cutoff)
        self.infoButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation))
        self.infoButton.clicked.connect(self.show_info_dialog)

    def accept(self):
        delete_uploads_args = ["delete-uploads"]
        if self.addUploadsCheckBox.isChecked():
            delete_uploads_args += ["-as", str(self.scoreCutoffInput.value())]
        self.parentWidget().launch_process(delete_uploads_args)
        super().accept()

    @QtCore.Slot()
    def enable_score_cutoff(self):
        self.scoreCutoffInput.setValue(85)
        self.scoreCutoffLabel.setEnabled(self.addUploadsCheckBox.isChecked())
        self.scoreCutoffInput.setEnabled(self.addUploadsCheckBox.isChecked())

    def show_info_dialog(self):
        QtWidgets.QMessageBox.information(
            self,
            "Add to Library",
            "Checking this box will make the tool attempt to add each album or song to your library from YouTube Music's"
            " online catalog before deleting it from your uploads. If a match could not be found, the album or song will"
            " remain in your uploads.\n\n"
            "Match score cutoff: A value closer to 100 will be more strict regarding matches when searching YTMusic for"
            " the song or album to add to your library.\n"
            "A value of 100 will basically only add exact matches.\n"
            "If you find that not many matches are being found, try lowering this value, but you may end up with albums"
            " in your library that are not exact matches.\n85 is a recommended value to start out with.",
        )
